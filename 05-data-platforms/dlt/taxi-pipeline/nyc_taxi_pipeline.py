"""NYC Taxi data pipeline using dlt REST API source."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def nyc_taxi_pipeline():
    """
    Fetch NYC taxi data from the REST API.
    
    The API returns paginated JSON with 1,000 records per page.
    Pagination stops automatically when an empty page is returned.
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "write_disposition": "replace",
        "resources": [
            {
                "name": "yellow_taxi",
                "endpoint": {
                    "path": "yellow_taxi",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name='nyc_taxi_pipeline',
    destination='duckdb',
    # `refresh="drop_sources"` ensures the data and the state is cleaned
    # on each `pipeline.run()`; remove the argument once you have a
    # working pipeline.
    #refresh="drop_sources",
    # show basic progress of resources extracted, normalized files and load-jobs on stdout
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(nyc_taxi_pipeline())
    print(load_info)  # noqa: T201
