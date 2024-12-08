import pytest

from app import RideAllocator


@pytest.fixture
def allocator():
    """
    Provides an instance of the RideAllocator class.
    """
    return RideAllocator()


def test_proportional_distribution(allocator):
    """
    Validates that the distribution is proportional to the requested sum.
    """
    approved = {"11 times sq": 350}
    requests = [
        {"company_name": "Microsoft", "destination": "11 times sq", "number_of_rides_requested": "300"},
        {"company_name": "Uber", "destination": "11 times sq", "number_of_rides_requested": "200"},
    ]
    distribution = allocator.distribute_approved_rides(approved, requests)

    # Check proportional allocation
    assert any(d["company_name"] == "Microsoft" and d["number_of_rides_approved"] == 200 for d in distribution)
    assert any(d["company_name"] == "Uber" and d["number_of_rides_approved"] == 100 for d in distribution)


def test_chunks_of_100(allocator):
    """
    Validates that distribution prioritizes chunks of 100 rides.
    """
    approved = {"11 times sq": 380}
    requests = [
        {"company_name": "Microsoft", "destination": "11 times sq", "number_of_rides_requested": "300"},
        {"company_name": "Uber", "destination": "11 times sq", "number_of_rides_requested": "200"},
    ]
    distribution = allocator.distribute_approved_rides(approved, requests)

    # Ensure distribution rounds down to the nearest 100
    assert all(d["number_of_rides_approved"] % 100 == 0 for d in distribution)
    total_approved = sum(d["number_of_rides_approved"] for d in distribution)
    assert total_approved <= 380  # Ensure no extra rides are distributed


def test_all_rides_distributed(allocator):
    """
    Validates that all approved rides are distributed.
    """
    approved = {"11 times sq": 300}
    requests = [
        {"company_name": "Microsoft", "destination": "11 times sq", "number_of_rides_requested": "200"},
        {"company_name": "Uber", "destination": "11 times sq", "number_of_rides_requested": "200"},
    ]
    distribution = allocator.distribute_approved_rides(approved, requests)

    total_distributed = sum(d["number_of_rides_approved"] for d in distribution)
    assert total_distributed == 300  # Ensure all approved rides are distributed


def test_no_over_allocation(allocator):
    """
    Validates that no company receives more rides than requested.
    """
    approved = {"11 times sq": 500}
    requests = [
        {"company_name": "Microsoft", "destination": "11 times sq", "number_of_rides_requested": "300"},
        {"company_name": "Uber", "destination": "11 times sq", "number_of_rides_requested": "200"},
    ]
    distribution = allocator.distribute_approved_rides(approved, requests)

    for d in distribution:
        original_request = next(
            req for req in requests if req["company_name"] == d["company_name"] and req["destination"] == d["destination"]
        )
        assert d["number_of_rides_approved"] <= int(original_request["number_of_rides_requested"])


def test_edge_case_no_requests(allocator):
    """
    Validates edge case where no requests are made for an approved destination.
    """
    approved = {"11 times sq": 300}
    requests = []
    distribution = allocator.distribute_approved_rides(approved, requests)

    # No rides should be distributed
    assert distribution == []


def test_edge_case_insufficient_rides(allocator):
    """
    Validates edge case where approved rides are insufficient for any company.
    """
    approved = {"11 times sq": 50}  # Less than a full chunk of 100
    requests = [
        {"company_name": "Microsoft", "destination": "11 times sq", "number_of_rides_requested": "300"},
        {"company_name": "Uber", "destination": "11 times sq", "number_of_rides_requested": "200"},
    ]
    distribution = allocator.distribute_approved_rides(approved, requests)

    # No rides should be allocated because they don't meet the minimum chunk size
    assert distribution == []
