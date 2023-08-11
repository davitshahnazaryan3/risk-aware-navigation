# Risk Aware Navigation

Demo of Risk-aware navigation system tailored for industries with a focus on accident prevention and insurance coverage

### TODOs
- [ ] dockerfiles and docker-compose files to be updated
- [ ] In progress: navigation App
- [ ] In progress: map creator

### Apps
- Component inventory
    - /inventory
- Risk calculation module
    - /src
- Risk-based navigation module, modified A*
    - /navigation

### Environmental variables
- MONGO_INITDB_ROOT_USERNAME
    - MongoDB username
- MONGO_INITDB_ROOT_PASSWORD
    - MongoDB password
- DATABASE_NAME
    - MongoDB database name
- NAVIGATION_IP_ADDRESS
    - IP address or container name of navigation app
- NAVIGATION_PORT
    - navigation app's port
- MAP_NAME
    - map name, currently "map_a", "map_b" to distinguish for a generated fictitious map, and a real map, respectively
- REDIS_HOST
    - redis server hostname
- REDIS_PORT
    - redis server port
- DB_TYPE
    - Database type, "remote" (cloud) or "local"

**Risk-aware-navigation:**
1. [Component inventory app](#inv)
2. [Component inventory database in NoSQL](#db)
3. [Structural risk calculation module](#str)
4. [Structural and environmental risk integration module](#combo)
5. [Patch request to risk mapping API for risks](#request)

**Required libraries**: 

        python -m pip install -r requirements.txt
        pip install "pymongo[srv]"

### 1. Map creator API
<details>
<a name="inv"></a>
<summary>Show/Hide</summary>
<br>

Component inventory creation app. Uses **Express.js** and **MongoDb** to generate component inventory and place them on the selected map. 

**To start the application, run the following command in your terminal:**

      cd inventory
      npm install
      node index.js

**Viewing API Documentation**

      localhost:{{PORT}}/api-docs

Replace {{PORT}} with the port number your application is running on.

</details>

### 2. Component inventory database in NoSQL
<details>
<a name="db"></a>
<summary>Show/Hide</summary>
<br>

**Structure of the component inventory database created via Mongo**

<p align="center">
  <img src="https://github.com/davitshahnazaryan3/risk-aware-navigation/blob/main/img/database.png" width=600>
</p>

* Note: **bold** stands for required arguments, <span style="color:red">red</span> stands for unique arguments. 

#### Definitions

* components - primary document consisting of all components
        
      _id - unique identifier
      name - name of the component
      description - description of the component
      reference - reference to the component (e.g., existing literature)
      cells - cell IDs of the map that include the component
      influence_cells - cell IDs of the map that include the influence zone of the component

* fragilityFunctions - description of the fragility function of the component

      _id - unique identifier
      imName - intensity measure name (e.g., PGA)
      unitOfMeasure - unit of measure of the intensity measure (e.g., g as in gravity acceleration or 9.81 m/s2)
      component - component identifier to which the function is tied to

* damageStates - description of the damage states characterising the component  - List of damage states
  
      _id - unique identifier
      name - name of the damage state (e.g., DS1)
      mean - mean of the distribution, must be in the same units as the fragilityFunctions
      dispersion - dispersion of the distribution
      component - component identifier to which the damage state is tied to

* coordinates - coordinates of the component within the map in cm - List of coordinates - may have multiple locations

      _id - unique identifier
      topLeft - top left coordinates in cm
      topRight - top right coordinates in cm
      bottomLeft - bottom left coordinates in cm
      bottomRight - bottom right coordinates in cm
      influenceRadius - influence radius of the component in cm, default to 0.0 cm
      component - component identifier to which the coordiantes are applied to

</details>

### 3. Risk calculation module
<details>
<a name="str"></a>
<summary>Show/Hide</summary>
<br>

**To start the application, run the following command in your terminal:**

      uvicorn src.app:app --port {{PORT}} --reload


**Takes as input:**
1. IM value - intensity measure value as float
2. Json filename - map of the plant as Path
    
      GET request to the API for the map with the name

**Runs**
3. assign_cells

      GET request to component directory
      Loop over each component and its coordinates
      Based on map information and coordinates calculate cell ID
      PATCH request to update the cell IDs
      
4. compute_risks

      GET request to component inventory for each component's fragility function and damage states
      Compute risk based on damage state and intensity measure
      Create a list of risks of the size of the number of cells
   

</details>


### 4. Structural and environmental risk integration module
<details>
<a name="combo"></a>
<summary>Show/Hide</summary>
<br>

**Runs**

1. Receive call from Environmental RIE
2. Combine with Structural RIE

</details>


### 5. Patch request to risk mapping API
<details>
<a name="request"></a>
<summary>Show/Hide</summary>
<br>

1. update_risks_rossini 
   
        Make PUT request to risk mapping api to update risks
        curl -X PUT id_address:port/map -H "Content-Type: application/json" -d 
        '{"personal_protection_equipment":"helmet",
        "map":[{"floor":0,"risk_values":[0,50,100]},{"floor":1,"risk_values":[2,3,4,5]}]}'
        
</details>

