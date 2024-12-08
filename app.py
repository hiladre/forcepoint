from flask import Flask, request, jsonify, send_file
import csv
from typing import Dict, List


class RideAllocator:
    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()

    @staticmethod
    def request_rides(requested_rides: Dict[str, int]) -> Dict[str, int]:
        """
        Simulated external API for requesting rides.
        """
        approved_rides = {}
        for destination, count in requested_rides.items():
            # Simulating approval of 70% of requests
            approved_rides[destination] = int(count * 0.7)
        return approved_rides

    @staticmethod
    def read_requests_from_csv(file_path: str) -> List[Dict[str, str]]:
        """
        Reads ride requests from a CSV file.
        """
        requests = []
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                requests.append(row)
        return requests

    @staticmethod
    def write_results_to_csv(results: List[Dict[str, str]], output_path: str):
        """
        Writes the distribution results to a CSV file.
        """
        with open(output_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["company_name", "destination", "number_of_rides_approved"])
            writer.writeheader()
            writer.writerows(results)

    @staticmethod
    def aggregate_requests(requests: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Aggregates requests by destination.
        """
        aggregated = {}
        for req in requests:
            destination = req["destination"]
            rides = int(req["number_of_rides_requested"])
            aggregated[destination] = aggregated.get(destination, 0) + rides
        return aggregated

    @staticmethod
    def distribute_approved_rides(approved: Dict[str, int], requests: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Distributes approved rides proportionally among requesting companies.
        """
        distribution = []
        requests_by_destination = {}

        # Group requests by destination
        for req in requests:
            destination = req["destination"]
            if destination not in requests_by_destination:
                requests_by_destination[destination] = []
            requests_by_destination[destination].append(req)

        # Distribute rides
        for destination, approved_rides in approved.items():
            if destination not in requests_by_destination:
                continue

            total_requested = sum(int(req["number_of_rides_requested"]) for req in requests_by_destination[destination])
            remaining_rides = approved_rides

            for req in requests_by_destination[destination]:
                company_name = req["company_name"]
                requested_rides = int(req["number_of_rides_requested"])

                # Proportional allocation rounded to nearest 100
                proportion = requested_rides / total_requested
                allocated_rides = int((approved_rides * proportion) // 100) * 100

                # Prevent over-allocation
                if allocated_rides > requested_rides:
                    allocated_rides = requested_rides

                remaining_rides -= allocated_rides
                if allocated_rides > 0:
                    distribution.append({
                        "company_name": company_name,
                        "destination": destination,
                        "number_of_rides_approved": allocated_rides
                    })

            # Distribute leftover rides in chunks of 100
            for req in requests_by_destination[destination]:
                if remaining_rides < 100:
                    break
                company_name = req["company_name"]
                requested_rides = int(req["number_of_rides_requested"])
                already_allocated = sum(
                    int(dist["number_of_rides_approved"])
                    for dist in distribution
                    if dist["company_name"] == company_name and dist["destination"] == destination
                )
                if already_allocated < requested_rides:
                    distribution.append({
                        "company_name": company_name,
                        "destination": destination,
                        "number_of_rides_approved": 100
                    })
                    remaining_rides -= 100

        return distribution

    def _setup_routes(self):
        """
        Configures Flask routes for the application.
        """
        @self.app.route("/allocate_rides", methods=["POST"])
        def allocate_rides():
            try:
                # Read input file
                file = request.files["file"]
                requests = self.read_requests_from_csv(file)

                # Aggregate requests
                aggregated_requests = self.aggregate_requests(requests)

                # Request approved rides from external API
                approved_rides = self.request_rides(aggregated_requests)

                # Distribute approved rides
                distribution = self.distribute_approved_rides(approved_rides, requests)

                # Write to output file
                output_path = "approved_rides.csv"
                self.write_results_to_csv(distribution, output_path)

                return send_file(output_path, as_attachment=True)

            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def run(self, **kwargs):
        """
        Runs the Flask application.
        """
        self.app.run(**kwargs)


if __name__ == "__main__":
    allocator = RideAllocator()
    allocator.run(debug=True)
