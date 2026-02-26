import unittest

import agent
from agent.workflow.db_providers import (
    DBWorkflowArticleContentProvider,
    DBWorkflowDataProvider,
    DBWorkflowMemoryProvider,
    DBWorkflowPersistenceProvider,
)


class BackendAgentWiringTest(unittest.TestCase):
    def test_init_agent_injects_db_providers(self):
        original_instance = agent._agent_instance
        try:
            agent._agent_instance = None
            workflow = agent.init_agent()

            self.assertIsInstance(workflow._data_provider, DBWorkflowDataProvider)
            self.assertIsInstance(
                workflow._persistence_provider, DBWorkflowPersistenceProvider
            )
            self.assertIsInstance(workflow._memory_provider, DBWorkflowMemoryProvider)
            self.assertIsInstance(
                workflow._article_content_provider, DBWorkflowArticleContentProvider
            )
        finally:
            agent._agent_instance = original_instance


if __name__ == "__main__":
    unittest.main()
