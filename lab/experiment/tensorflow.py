import json
import pathlib
from typing import List, Optional

import numpy as np
import tensorflow as tf

from lab import tf_util, util, experiment, logger, tf_compat
from lab.logger_class import tensorboard_writer, CheckpointSaver


class Checkpoint(CheckpointSaver):
    max_step: Optional[int]
    __variables: Optional[List[tf.Variable]]

    def __init__(self, path: pathlib.PurePath):
        self.path = path
        self.max_step = None
        self.__variables = None

    def set_variables(self, variables: List[tf.Variable]):
        """
        ## Set variable for saving and loading
        """
        self.__variables = variables

    def save(self, global_step, args):
        self._save(global_step, args[0])

    def _save(self, global_step, session: tf.Session):
        """
        ## Save model as a set of numpy arrays
        """

        checkpoints_path = pathlib.Path(self.path)
        if not checkpoints_path.exists():
            checkpoints_path.mkdir()

        checkpoint_path = checkpoints_path / str(global_step)
        assert not checkpoint_path.exists()

        checkpoint_path.mkdir()

        values = session.run(self.__variables)

        # Save each variable
        files = {}
        for variable, value in zip(self.__variables, values):
            file_name = tf_util.variable_name_to_file_name(
                tf_util.strip_variable_name(variable.name))
            file_name = f"{file_name}.npy"
            files[variable.name] = file_name

            np.save(str(checkpoint_path / file_name), value)

        # Save header
        with open(str(checkpoint_path / "info.json"), "w") as f:
            f.write(json.dumps(files))

        # Delete old checkpoints
        for c in checkpoints_path.iterdir():
            if c.name != checkpoint_path.name:
                util.rm_tree(c)

    def load(self, session: tf.Session):
        """
        ## Load model as a set of numpy arrays
        """

        checkpoints_path = pathlib.Path(self.path)
        if not checkpoints_path.exists():
            return False

        max_step = -1
        for c in checkpoints_path.iterdir():
            max_step = max(max_step, int(c.name))

        if max_step < 0:
            return False

        checkpoint_path = checkpoints_path / str(max_step)

        with open(str(checkpoint_path / "info.json"), "r") as f:
            files = json.loads(f.readline())

        # Load each variable
        for variable in self.__variables:
            file_name = files[variable.name]
            value = np.load(str(checkpoint_path / file_name))
            ph = tf.placeholder(value.dtype,
                                shape=value.shape,
                                name=f"{tf_util.strip_variable_name(variable.name)}_ph")

            assign_op = tf.assign(variable, ph)
            session.run(assign_op, feed_dict={ph: value})

        self.max_step = max_step

        return True


class Experiment(experiment.Experiment):
    """
    ## Experiment

    Each experiment has different configurations or algorithms.
    An experiment can have multiple trials.
    """

    __checkpoint_saver: Checkpoint

    def __init__(self, *,
                 name: str,
                 python_file: str,
                 comment: str,
                 check_repo_dirty: Optional[bool] = None,
                 is_log_python_file: Optional[bool] = None):
        """
        ### Create the experiment

        :param name: name of the experiment
        :param python_file: `__file__` that invokes this. This is stored in
         the experiments list.
        :param comment: a short description of the experiment
        :param check_repo_dirty: whether not to start the experiment if
         there are uncommitted changes.

        The experiments log keeps track of `python_file`, `name`, `comment` as
         well as the git commit.

        Experiment maintains the locations of checkpoints, logs, etc.
        """

        super().__init__(name=name,
                         python_file=python_file,
                         comment=comment,
                         check_repo_dirty=check_repo_dirty,
                         is_log_python_file=is_log_python_file)

    def _create_checkpoint_saver(self):
        self.__checkpoint_saver = Checkpoint(self.info.checkpoint_path)
        return self.__checkpoint_saver

    def create_writer(self, session: tf_compat.Session):
        """
        ## Create TensorFlow summary writer
        """
        logger.add_writer(tensorboard_writer.Writer(
            tf_compat.summary.FileWriter(str(self.info.summary_path), session.graph)))

    def set_variables(self, variables: List[tf.Variable]):
        """
        ## Set variable for saving and loading
        """
        self.__checkpoint_saver.set_variables(variables)

    def start_train(self, session: tf.Session, is_init: bool = True):
        """
        ## Start experiment

        Load a checkpoint or reset based on `global_step`.
        """

        global_step = 0

        if not is_init:
            # load checkpoint if we are starting from middle
            with logger.section("Loading checkpoint") as m:
                is_successful = self.__checkpoint_saver.load(session)
                logger.set_successful(is_successful)
                if is_successful:
                    global_step = self.__checkpoint_saver.max_step

        self._start(global_step)

        if global_step == 0:
            # initialize variables and clear summaries if we are starting from scratch
            with logger.section("Clearing summaries"):
                self.clear_summaries()
            with logger.section("Clearing checkpoints"):
                self.clear_checkpoints()
            with logger.section("Initializing variables"):
                tf_util.init_variables(session)

        self.create_writer(session)

    def start_replay(self, session: tf.Session):
        """
        ## Start replaying experiment

        Load a checkpoint or reset based on `global_step`.
        """

        with logger.section("Loading checkpoint") as m:
            m.is_successful = self.__checkpoint_saver.load(session)
