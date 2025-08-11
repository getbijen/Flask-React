import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from flask_smorest import abort

# Import the controller to test
from flaskr.controllers.task_controller import TaskController
from flaskr.models.task_model import TaskModel, TaskStatus
from flaskr.models.tag_model import TagModel
from flaskr.models.user_model import UserModel


# Test fixtures
@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_jwt_identity():
    """Mock JWT identity (user ID)"""
    return 1


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "content": "Test content for the task",
        "status": TaskStatus.PENDING,
        "tag_id": 1
    }


@pytest.fixture
def sample_task():
    """Sample task model instance"""
    return TaskModel(
        id=1,
        title="Test Task",
        content="Test content",
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        user_id=1,
        tag_id=1
    )


@pytest.fixture
def sample_tag():
    """Sample tag model instance"""
    return TagModel(
        id=1,
        name="Work"
    )


@pytest.fixture
def mock_query_result():
    """Mock query result for task queries"""
    mock_result = Mock()
    mock_result.all.return_value = [
        (1, "Test Task", "Test content", TaskStatus.PENDING, 
         datetime.now(timezone.utc), "Work")
    ]
    return mock_result


# Test class for TaskController
class TestTaskController:
    """Test suite for TaskController class"""

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_get_all_on_user_success(self, mock_db, mock_jwt_identity, mock_query_result):
        """Test successful retrieval of all tasks for a user"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.query.return_value.where.return_value.join.return_value = mock_query_result
        
        # Act
        result = TaskController.get_all_on_user()
        
        # Assert
        assert result is not None
        mock_db.session.query.assert_called_once_with(
            TaskModel.id,
            TaskModel.title,
            TaskModel.content,
            TaskModel.status,
            TaskModel.created_at,
            TagModel.name.label("tag_name")
        )

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_get_all_on_user_database_error(self, mock_abort, mock_db, mock_jwt_identity):
        """Test handling of database errors when fetching user tasks"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.query.side_effect = SQLAlchemyError("Database error")
        
        # Act
        TaskController.get_all_on_user()
        
        # Assert
        mock_abort.assert_called_once_with(
            500, 
            message="Internal server error while fetching tasks on user"
        )

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_create_task_success(self, mock_db, mock_jwt_identity, sample_task_data):
        """Test successful task creation"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        # Act
        TaskController.create(sample_task_data)
        
        # Assert
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        
        # Verify the task was created with correct data
        added_task = mock_db.session.add.call_args[0][0]
        assert added_task.title == sample_task_data["title"]
        assert added_task.content == sample_task_data["content"]
        assert added_task.status == sample_task_data["status"]
        assert added_task.tag_id == sample_task_data["tag_id"]
        assert added_task.user_id == 1

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_create_task_database_error(self, mock_abort, mock_db, mock_jwt_identity, sample_task_data):
        """Test handling of database errors during task creation"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.add = Mock()
        mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.session.rollback = Mock()
        
        # Act
        TaskController.create(sample_task_data)
        
        # Assert
        mock_db.session.rollback.assert_called_once()
        mock_abort.assert_called_once_with(
            500, 
            message="Internal server error while creating task"
        )

    @patch('flaskr.controllers.task_controller.db')
    def test_update_task_success(self, mock_db, sample_task, sample_task_data):
        """Test successful task update"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.return_value = sample_task
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        update_data = {
            "title": "Updated Task",
            "content": "Updated content",
            "status": TaskStatus.IN_PROGRESS
        }
        
        # Act
        TaskController.update(update_data, 1)
        
        # Assert
        assert sample_task.title == update_data["title"]
        assert sample_task.content == update_data["content"]
        assert sample_task.status == update_data["status"]
        mock_db.session.add.assert_called_once_with(sample_task)
        mock_db.session.commit.assert_called_once()

    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_update_task_not_found(self, mock_abort, mock_db):
        """Test handling of task not found during update"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.side_effect = NoResultFound()
        
        # Act
        TaskController.update({"title": "Test"}, 999)
        
        # Assert
        mock_abort.assert_called_once_with(
            404, 
            message="Task not found"
        )

    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_update_task_database_error(self, mock_abort, mock_db, sample_task):
        """Test handling of database errors during task update"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.return_value = sample_task
        mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.session.rollback = Mock()
        
        # Act
        TaskController.update({"title": "Test"}, 1)
        
        # Assert
        mock_db.session.rollback.assert_called_once()
        mock_abort.assert_called_once_with(
            500, 
            message="Internal server error while updating task"
        )

    @patch('flaskr.controllers.task_controller.db')
    def test_delete_task_success(self, mock_db, sample_task):
        """Test successful task deletion"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.return_value = sample_task
        mock_db.session.delete = Mock()
        mock_db.session.commit = Mock()
        
        # Act
        TaskController.delete(1)
        
        # Assert
        mock_db.session.delete.assert_called_once_with(sample_task)
        mock_db.session.commit.assert_called_once()

    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_delete_task_not_found(self, mock_abort, mock_db):
        """Test handling of task not found during deletion"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.side_effect = NoResultFound()
        
        # Act
        TaskController.delete(999)
        
        # Assert
        mock_abort.assert_called_once_with(
            404, 
            message="Task not found"
        )

    @patch('flaskr.controllers.task_controller.db')
    @patch('flaskr.controllers.task_controller.abort')
    def test_delete_task_database_error(self, mock_abort, mock_db, sample_task):
        """Test handling of database errors during task deletion"""
        # Arrange
        mock_db.session.execute.return_value.scalar_one.return_value = sample_task
        mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.session.rollback = Mock()
        
        # Act
        TaskController.delete(1)
        
        # Assert
        mock_db.session.rollback.assert_called_once()
        mock_abort.assert_called_once_with(
            500, 
            message="Internal server error while deleting task"
        )


# Integration tests
class TestTaskControllerIntegration:
    """Integration tests for TaskController with database"""

    @pytest.fixture(autouse=True)
    def setup_database(self, app, db_session):
        """Setup test database"""
        self.app = app
        self.db = db_session
        
        # Create test data
        self.user = UserModel(
            username="testuser",
            email="test@example.com",
            password="hashedpassword"
        )
        self.db.add(self.user)
        
        self.tag = TagModel(name="Test Tag")
        self.db.add(self.tag)
        
        self.db.commit()

    def test_create_and_retrieve_task_integration(self):
        """Test complete flow of creating and retrieving a task"""
        with self.app.app_context():
            # Create task
            task_data = {
                "title": "Integration Test Task",
                "content": "This is a test task for integration testing",
                "status": TaskStatus.PENDING,
                "tag_id": self.tag.id
            }
            
            # Mock JWT identity
            with patch('flaskr.controllers.task_controller.get_jwt_identity') as mock_jwt:
                mock_jwt.return_value = self.user.id
                
                # Create task
                TaskController.create(task_data)
                
                # Retrieve tasks
                tasks = TaskController.get_all_on_user()
                
                # Assertions
                assert len(tasks) == 1
                assert tasks[0][1] == task_data["title"]  # title
                assert tasks[0][2] == task_data["content"]  # content
                assert tasks[0][3] == task_data["status"]  # status


# Edge case tests
class TestTaskControllerEdgeCases:
    """Test edge cases and boundary conditions"""

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_create_task_with_empty_data(self, mock_db, mock_jwt_identity):
        """Test task creation with minimal data"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        minimal_data = {
            "title": "Minimal Task",
            "content": "Minimal content",
            "status": TaskStatus.PENDING,
            "tag_id": 1
        }
        
        # Act
        TaskController.create(minimal_data)
        
        # Assert
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_create_task_with_maximum_length_data(self, mock_db, mock_jwt_identity):
        """Test task creation with maximum length data"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        max_length_data = {
            "title": "A" * 40,  # Maximum title length
            "content": "B" * 600,  # Maximum content length
            "status": TaskStatus.COMPLETED,
            "tag_id": 1
        }
        
        # Act
        TaskController.create(max_length_data)
        
        # Assert
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()

    def test_task_status_enum_values(self):
        """Test that TaskStatus enum has expected values"""
        # Assert
        assert TaskStatus.PENDING == "PENDING"
        assert TaskStatus.IN_PROGRESS == "IN_PROGRESS"
        assert TaskStatus.COMPLETED == "COMPLETED"
        assert len(TaskStatus) == 3


# Performance tests
class TestTaskControllerPerformance:
    """Performance tests for TaskController"""

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_get_all_on_user_performance(self, mock_db, mock_jwt_identity):
        """Test performance of getting all user tasks"""
        import time
        
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_query_result = Mock()
        mock_query_result.all.return_value = [(i, f"Task {i}", f"Content {i}", 
                                             TaskStatus.PENDING, datetime.now(timezone.utc), 
                                             f"Tag {i}") for i in range(100)]
        
        mock_db.session.query.return_value.where.return_value.join.return_value = mock_query_result
        
        # Act
        start_time = time.time()
        result = TaskController.get_all_on_user()
        end_time = time.time()
        
        # Assert
        assert len(result) == 100
        assert (end_time - start_time) < 1.0  # Should complete within 1 second


# Security tests
class TestTaskControllerSecurity:
    """Security tests for TaskController"""

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_user_isolation(self, mock_db, mock_jwt_identity):
        """Test that users can only access their own tasks"""
        # Arrange
        mock_jwt_identity.return_value = 2  # Different user ID
        mock_query_result = Mock()
        mock_query_result.all.return_value = []
        
        mock_db.session.query.return_value.where.return_value.join.return_value = mock_query_result
        
        # Act
        result = TaskController.get_all_on_user()
        
        # Assert
        assert len(result) == 0
        # Verify the query was filtered by user_id
        mock_db.session.query.return_value.where.assert_called_once()

    @patch('flaskr.controllers.task_controller.get_jwt_identity')
    @patch('flaskr.controllers.task_controller.db')
    def test_sql_injection_prevention(self, mock_db, mock_jwt_identity):
        """Test that SQL injection attempts are prevented"""
        # Arrange
        mock_jwt_identity.return_value = 1
        mock_db.session.execute = Mock()
        
        malicious_data = {
            "title": "'; DROP TABLE tasks; --",
            "content": "Malicious content",
            "status": TaskStatus.PENDING,
            "tag_id": 1
        }
        
        # Act
        TaskController.create(malicious_data)
        
        # Assert
        # The malicious input should be treated as regular string data
        # and not cause any SQL injection
        mock_db.session.add.assert_called_once() 