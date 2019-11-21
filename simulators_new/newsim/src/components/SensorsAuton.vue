<template>
  <div class="wrap">
    <SensorItem v-bind='sensor' v-for='(sensor, index) in sensorData' :key='index'/>
    <div v-if='sensorData.length%2==1' class='box' ></div>
  </div>
</template>

<script>
import SensorItem from './SensorItem.vue'
import Checkbox from './Checkbox.vue'
import {mapMutations} from 'vuex'

export default {
  name: 'Sensors',

  data() {
    return {
      rawData: {
        latitude_deg: 0,
        latitude_min: 0,
        longitude_deg: 0,
        longitude_min: 0,
        bearing_deg: 0,
        speed: 0
      }
    }
  },

  computed: {
    color: function () {
      return this.recording ? 'green' : 'red'
    },
    sensorData: function () {
      return [
        {
          name: 'GPS',
          value: this.rawData.latitude_deg,
          value: this.rawData.latitude_min,
          value: this.rawData.longitude_deg,
          value: this.rawData.longitude_min,
          value: this.rawData.bearing_deg,
          value: this.rawData.speed
        },
        {
          name: 'Moisture',
          value: this.rawData.moisture
        },
        {
          name: 'Soil Conductivity',
          value: this.rawData.conductivity,
          unit: 'µS/cm'
        },
        {
          name: 'pH',
          value: this.rawData.pH
        },
        {
          name: 'Oxygen',
          value: this.rawData.O2,
          unit: 'ppm'
        },
        {
          name: 'Carbon Dioxide',
          value: this.rawData.CO2,
          unit: 'ppm'
        },
        {
          name: 'CPU Temperature',
          value: this.rawData.bcpu_temp / 1000,
          unit: 'ºC'
        },
        {
          name: 'GPU Temperature',
          value: this.rawData.gpu_temp / 1000,
          unit: 'ºC'
        },
        {
          name: 'Overall Board Temperature',
          value: this.rawData.tboard_temp / 1000,
          unit: 'ºC'
        }
      ]
    }
  },

  created: function() {
    this.$parent.subscribe('/gps', (msg) => {
      this.rawData = Object.assign(this.rawData, msg)
    })

    this.$parent.subscribe('/temperature', (msg) => {
      this.rawData = Object.assign(this.rawData, msg)
    })
  },

  components: {
    Checkbox,
    SensorItem
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped>
.wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(auto-fill, 35px);
  height: 100%;
}

.white-text{
  color: white;
}

.box {
  padding: 0px;
  padding-left: 5px;
  padding-right: 5px;
  border: none;
}

.green {
  background-color: green;
}

.red {
  background-color: red;
}
</style>
