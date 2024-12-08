import pytest

from app import RideAllocator


@pytest.fixture
def client():
    """
    Sets up the Flask test client for the RideAllocator app.
    """
    allocator = RideAllocator()
    allocator.app.config["TESTING"] = True
    with allocator.app.test_client() as client:
        yield client


@pytest.fixture
def sample_csv(tmp_path):
    """
    Creates a temporary CSV file for testing ride requests.
    """
    file_path = tmp_path / "requests.csv"
    with open(file_path, "w") as file:
        file.write("company_name,destination,number_of_rides_requested\n")
        file.write("Microsoft,11 times sq,300\n")
        file.write("Uber,11 times sq,200\n")
        file.write("Facebook,770 Broadway,400\n")
    return str(file_path)


@pytest.fixture
def output_csv_path(tmp_path):
    """
    Returns a path for the output CSV file.
    """
    return tmp_path / "approved_rides.csv"
