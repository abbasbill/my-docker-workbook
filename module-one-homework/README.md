# Module_one-Homework
Data-engineering-zoomcamp module 1 homework: Docker &amp; SQL

## Question 1. Understanding Docker images
### a. Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.
#### Solution
```bash
docker run -it --rm --entrypoint=bash python:3.13 
```
This runs an interactive bash shell inside a Python 3.13 container that gets deleted after exiting.  

Understanding each part of the command:
* docker run: Creates and starts a new container
* -it: Two flags combined:
* -i (interactive): Keeps STDIN open so you can type commands
* -t (tty): Allocates a pseudo-terminal for a proper shell experience
* --rm: Automatically removes the container when it exits (cleanup)
* --entrypoint=bash: Overrides the default command the container runs with bash
* python:3.13: The Docker image to use (Python version 3.13)

What happens:
Instead of dropping into a Python interpreter (the default for python images), you get a bash shell where you can run any commands, install packages, explore the filesystem, etc. When you type exit, the container stops and is automatically deleted.  

This is useful for debugging, testing, or exploring what's inside a Python container environment. 


### b. What's the version of `pip` in the image?

- 25.3
- 24.3.1
- 24.2.1
- 23.3.1
  #### Solution
  To check the pip version, we run:
```bash
  pip --version
```
This output - 25.3 as the pip version as seen in the image below
  
<img width="689" height="354" alt="image" src="https://github.com/user-attachments/assets/6c4b7460-5255-4274-98cd-72def1c42040" />

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- db:5432

#### Solution
we copied the above code block and created a docker-compose.yaml file with it in our project repository and run the command below in our bash terminal from within our project root folder where the docker-compose.yaml file is housed:  
```bash
docker compose up -d
``` 

This uses our docker-compose.yaml file to sets up a dockerize local database environment with two services: PostgreSQL and pgAdmin.  

The pgadmin service (database management tool) Provides a web-based interface to manage our PostgreSQL database which we can access at http://localhost:8080 from our browser!   

Using Login credentials as defined in our docker-compose.yaml file
* email: pgadmin@pgadmin.com,
* password: pgadmin  


we were then able to Connect to our postgres database from pgAdmin (the web interface at localhost:8080), using the parameters:

* Host: db (not localhost or 127.0.0.1, because pgAdmin is inside Docker)  

* Port: 5432 (not 5433, because inside Docker it uses the internal port)  

* Username: postgres  

* Password: postgres  


## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- 7,853
- 8,007
- 8,254
- 8,421

### Solution
By qurying our database with the query below, the number of trips in November 2025 between '2025-11-01' and '2025-12-01', exclusive of the upper bound that had a trip distance less than or equal to 1 mile is `8,007`
```sql
SELECT COUNT(1) as trip_distance_less_than_one_mile
FROM public."green_tripdata_2025-11"
WHERE lpep_pickup_datetime >= '2025-11-01' 
AND lpep_pickup_datetime < '2025-12-01'
AND trip_distance <= 1;
```
* This returns 8,007
<img width="517" height="498" alt="queryii" src="https://github.com/user-attachments/assets/5ba415ba-389b-4087-a69a-6debe13a24c2" />

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

- 2025-11-14
- 2025-11-20
- 2025-11-23
- 2025-11-25
### Solution
We determine the pick up day with the longest trip distance? Only considering trips with trip_distance less than 100 miles (to exclude data errors) with the query:  
```sql
SELECT
    DATE(lpep_pickup_datetime) as pickup_day_of_max_trip_distance,
	trip_distance
FROM public."green_tripdata_2025-11"
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1;
```
* This returns `2025-11-14` as the date of the day with the longest trip distance being 88.03 miles (only considering the dataset with less than 100 miles trip_distance to account for data errors)
<img width="707" height="471" alt="quryiii" src="https://github.com/user-attachments/assets/079a9a84-4865-4776-b8d5-426d0ff52b6c" />

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- East Harlem North
- East Harlem South
- Morningside Heights
- Forest Hills

### Solution
The pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025 is:  
- `East Harlem North` having `434` trips!
<img width="636" height="504" alt="query_v" src="https://github.com/user-attachments/assets/368913d5-63cc-4867-9b70-698d91f92693" />

## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?
- JFK Airport
- Yorkville West
- East Harlem North
- LaGuardia Airport

### Solution
The passengers picked up in the zone named "East Harlem North" in November 2025, with the drop off zone that had the largest tip is:
- `Yorkville West` having total tip of `81.89`
<img width="611" height="612" alt="image" src="https://github.com/user-attachments/assets/2ac305b2-3b7f-4677-8809-fb892fe86f5c" />

## Question 7. Terraform Workflow
Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm

### Solution
The sequence of operation that respectively describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform is:
   
-> terraform init, terraform apply -auto-approve, terraform destroy
