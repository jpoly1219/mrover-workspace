<template>
  <div class="wrap">
    <div class="box">
      Name: <input v-model="name"><br>
      <input v-model="lat">ºN
      <input v-model="lon">ºW
      <button v-on:click="parseWaypoint()">Add Waypoint</button>
      <button v-on:click="dropWaypoint()">Drop Waypoint</button>
      <Checkbox v-bind:name="'Add waypoint by mouseclick?'" v-on:toggle="toggleWaypointCheckbox()" />
    </div>
    <div class="box">
      <Checkbox ref="checkbox" v-bind:name="'Autonomy Mode'" v-on:toggle="toggleAutonMode($event) "/><br>
      <span>
        Navigation State: {{nav_status.nav_state_name}}<br>
        Waypoints Traveled: {{nav_status.completed_wps}}/{{nav_status.total_wps}}<br>
        Missed Waypoints: {{nav_status.missed_wps}}/{{nav_status.total_wps}}<br>
        Tennis Balls: {{nav_status.found_tbs}}/{{nav_status.total_tbs}} 
      </span>
    </div>
    <div class="box">
      <h3>All Waypoints</h3>
      <draggable v-model="storedWaypoints" class="dragArea" draggable=".item'">
        <WaypointItem v-for="waypoint, i in storedWaypoints" :key="i" v-bind:waypoint="waypoint" v-bind:list="0" v-bind:index="i" v-on:delete="deleteItem($event)" v-on:toggleSearch="toggleSearch($event)" v-on:toggleGate="toggleGate($event)" v-on:add="addItem($event)" v-on:convertDMS="convertWaypointDMS($event)"/>
      </draggable>
    </div>
    <div class="box">
      <h3>Current Course</h3>
      <draggable v-model="route" class="dragArea" draggable=".item'">
        <WaypointItem v-for="waypoint, i in route" :key="i" v-bind:waypoint="waypoint" v-bind:list="1" v-bind:index="i" v-on:delete="deleteItem($event)" v-on:toggleSearch="toggleSearch($event)" v-on:toggleGate="toggleGate($event)" v-on:add="addItem($event)" v-on:convertDMS="convertWaypointDMS($event)"/>
      </draggable>
    </div>
  </div>
</template>

<script>
import Checkbox from './Checkbox.vue'
import draggable from 'vuedraggable'
import WaypointItem from './WaypointItem_Auton.vue'
import {mapMutations, mapGetters} from 'vuex'
import _ from 'lodash';
import fnvPlus from 'fnv-plus';
import L from 'leaflet'

let interval;

export default {

  props: {
    odom: {
      type: Object,
      required: true
    },
  },

  data () {
    return {
      name: "",
      lon: "",
      lat: "",

      nav_status: {
        nav_state_name: "Off",
        completed_wps: 0,
        missed_wps: 0,
        total_wps: 0
      },

      storedWaypoints: [],
      route: [],
      waypointCheckbox: false
    }
  },

  beforeDestroy: function () {
    window.clearInterval(interval);
  },

  created: function () {

    this.$parent.subscribe('/nav_status', (msg) => {
      this.nav_status = msg
    })

    this.$root.$on("e", coords => {
      this.lat = coords[0].toString();
      this.lon = (-1*coords[1]).toString();
      this.name = "Waypoint " + _.size(this.storedWaypoints);
      console.log("wpc: " + this.waypointCheckbox);
      if(this.waypointCheckbox){
        typeof(this.lat);
        typeof(this.lon);
        this.parseWaypoint();
      }
    })

    interval = window.setInterval(() => {
        if(this.auton_enabled && this.nav_status.nav_state_name === 'Done'){
          this.$refs.checkbox.toggleAndEmit()
        }

        this.$parent.publish('/auton', {type: 'AutonState', is_auton: this.auton_enabled})

        let course = {
            num_waypoints: this.route.length,
            waypoints: _.map(this.route, (waypoint) => {
              let lat = waypoint.latLng.lat
              let lng = waypoint.latLng.lng
              let latitude_deg = Math.trunc(lat)
              let latitude_min = (lat - latitude_deg) * 60
              let longitude_deg = Math.trunc(lng)
              let longitude_min = (lng - longitude_deg) * 60
              return {
                  type: "Waypoint",
                  search: waypoint.search,
                  gate: waypoint.gate,
                  odom: {
                      latitude_deg: latitude_deg,
                      latitude_min: latitude_min,
                      longitude_deg: longitude_deg,
                      longitude_min: longitude_min,
                      bearing_deg: 0,
                      type: "Odometry"
                  }
              }
            })
        };
        course.hash = fnvPlus.fast1a52(JSON.stringify(course));
        course.type = 'Course'
        this.$parent.publish('/course', course)

    }, 100);
  },

  methods: {
    ...mapMutations('autonomy',{
      setRoute: 'setRoute',
      setWaypointList: 'setWaypointList',
      setAutonMode: 'setAutonMode',
      //setWaypointCheckbox: 'setWaypointCheckbox'
    }),

    deleteItem: function (payload) {
      if(payload.list === 0) {
        this.storedWaypoints.splice(payload.index, 1)
      } else if(payload.list === 1) {
        this.route.splice(payload.index, 1)
      }
    },

    // Add item from all waypoints div to current waypoints div
    addItem: function (payload) {
       if(payload.list === 0) {
        this.route.push(this.storedWaypoints[payload.index])
      } else if(payload.list === 1) {
        this.storedWaypoints.push(this.route[payload.index])
      }

    },


    toggleSearch: function (payload) {
      if(payload.list === 0) {
        this.storedWaypoints[payload.index].search = !this.storedWaypoints[payload.index].search
      } else if(payload.list === 1) {
        this.route[payload.index].search = !this.route[payload.index].search
      }
    },

     toggleGate: function (payload) {
      if(payload.list === 0) {
        this.storedWaypoints[payload.index].gate = !this.storedWaypoints[payload.index].gate
      } else if(payload.list === 1) {
        this.route[payload.index].gate = !this.route[payload.index].gate
      }
    },

    addWaypoint: function (lat, lon) {
      this.storedWaypoints.push({
        name: this.name,
        latLng: L.latLng(lat, lon),
        search: false,
        gate: false
      })
    },

    dropWaypoint: function () {
      let lat = this.odom.latitude_deg + this.odom.latitude_min/60
      let lon = this.odom.longitude_deg + this.odom.longitude_min/60
      this.addWaypoint(lat, lon)
    },

    convertWaypointDMS: function(payload) {
       const parseCoordinate = function (input) {
        const nums = input.split(" ")
        switch (nums.length) {
          case 1:z
            return parseFloat(nums[0])
          case 2:
            return parseFloat(nums[0]) + parseFloat(nums[1])/60
          case 3:
            return parseFloat(nums[0]) + parseFloat(nums[1])/60 + parseFloat(nums[2])/3600
          default:
            return 0
        }
      }

      this.addWaypoint(parseCoordinate(payload.lat), -parseCoordinate(payload.lon))  

      if(payload.list === 0) {
        this.storedWaypoints.splice(payload.index, 1)
      } else if(payload.list === 1) {
        this.route.splice(payload.index, 1)
      } 
      
    },

    parseWaypoint: function () {
      const parseCoordinate = function (input) {
        const nums = input.split(" ")
        switch (nums.length) {
          case 1:
            return parseFloat(nums[0])
          case 2:
            return parseFloat(nums[0]) + parseFloat(nums[1])/60
          case 3:
            return parseFloat(nums[0]) + parseFloat(nums[1])/60 + parseFloat(nums[2])/3600
          default:
            return 0
        }
      }

      this.addWaypoint(parseCoordinate(this.lat), -parseCoordinate(this.lon))
    },

   toggleAutonMode: function (val) {
      this.setAutonMode(val)
    },

   toggleWaypointCheckbox: function(val){
     console.log("toggleWPCheckbox " + this.waypointCheckbox + val)
     this.waypointCheckbox = !this.waypointCheckbox
     //this.setWaypointCheckbox(val)
    },
   },

  watch: {
    route: function (newRoute) {
      this.setRoute(newRoute)
    },

    storedWaypoints: function (newList) {
      this.setWaypointList(newList)
    }
  },

  computed: {
    ...mapGetters('autonomy', {
      auton_enabled: 'autonEnabled',
    })
  },

  components: {
    draggable,
    WaypointItem,
    Checkbox
  }

}
</script>

<style scoped>

  .wrap {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 7rem 1fr;
    grid-gap: 6px;
    height: 100%;
  }

  .dragArea {
    height: 100%;
  }

  .box {
    border-radius: 5px;
    padding: 10px;
    border: 1px solid black;

    overflow: auto;
  }
</style>
