__author__ = 'Bohdan Mushkevych'

from db.dao.step_dao import StepDao


class FlowGraphNode(object):
    def __init__(self, name, step_class, dependent_on_names):
        self.name = name
        self.step_class = step_class
        self.dependent_on_names = dependent_on_names
        self.step_instance = None
        self.execution_cluster = None
        self.step_dao = None
        self.logger = None

    def set_context(self, context, execution_cluster):
        self.context = context
        self.execution_cluster = execution_cluster

        log_file = os.path.join(context.settings['log_directory'], '{0}.log'.format(self.name))
        self.logger = Logger(log_file, self.name)
        self.step_dao = StepDao(self.logger)

    def reset_db_state(self):
        """ erase any existing records for given Step. Write new one instead """
        pass

    def run(self, context, execution_cluster):
        self.set_context(context, execution_cluster)
        self.reset_db_state()

        self.step_instance = self.step_class()
        self.step_instance.do_pre()
        if not self.step_instance.is_pre_completed:
            return self.step_instance.is_complete


        try:
            step_state = execution_cluster.run_pig_step(
                os.path.join(context.settings.settings['s3_pig_lib_path'], self.step_instance.pig_script),
                table_name=step_name,
                s3_input_path='s3://synergy',
                s3_output_path=context.settings.settings['s3_output_bucket'])
            self.step_instance.is_pig_completed = True if step_state else False
        except Exception:
            self.logger.error('Exception on step for {0} table'.format(step_name), exc_info=True)
            self.step_instance.is_pig_completed = False

        if not self.step_instance.is_pig_completed:
            return self.step_instance.is_complete

        self.step_instance.do_post()
        return self.step_instance.is_complete
