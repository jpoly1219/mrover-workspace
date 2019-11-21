<template>
  <div class="wrap">
    <p>
      Current GPS reading: {{ GPS.latitude_deg }}º {{ Math.floor(GPS.latitude_min) }}' {{ ((GPS.latitude_min % 1)*60).toFixed(4) }}" N by {{ -GPS.longitude_deg }}º {{ -Math.ceil(GPS.longitude_min) }}' {{ -((GPS.longitude_min % 1)*60).toFixed(4) }}" W bearing {{ GPS.bearing_deg.toFixed(2) }} speed: {{ GPS.speed }}
    </p>
  </div>
</template>

<script>
export default {
  props: {
    gps: {
      type: Object,
      required: true
    },
  }
}
</script>

<style scoped>
  .wrap {
      padding: 0px;
      padding-left: 5px;
      padding-right: 5px;
      border: none;
  }
</style>
