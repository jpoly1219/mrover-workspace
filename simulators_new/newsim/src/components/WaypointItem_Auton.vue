<template>
  <div class="waypoint-item">
    <div class="name">
      <p>{{waypoint.name}}</p>
    </div>
    <div class="location">
      <p>{{waypoint.latLng.lat}}ºN, {{-waypoint.latLng.lng}}ºW</p>
      <p>{{waypoint.latLng.lat}}ºN, {{-waypoint.latLng.lng}}ºW</p>
    </div>
    <div class="buttons">
      <button class="red" v-on:click="$emit('add', {'list': list, 'index': index})">Add</button>
      <button v-bind:class="[waypoint.search ? 'green' : 'red']" v-on:click="$emit('toggleSearch', {'list': list, 'index': index})">Search</button>
      <button v-bind:class="[waypoint.gate ? 'green' : 'red']" v-on:click="$emit('toggleGate', {'list': list, 'index': index})">Gate</button>
      <button class="red" v-on:click="$emit('delete', {'list': list, 'index': index})">Delete</button>
      <button class="red" v-on:click="$emit('convertDMS', {'list': list, 'index': index})">DMS</button>
    </div>
  </div>
</template>

<script>
export default {

  props: {
    waypoint: {
      type: Object,
      required: true
    },

    list: {
      type: Number,
      required: true
    },

    index: {
      type: Number,
      required: true
    }
  }

}
</script>

<style scoped>
  .waypoint-item {
    display: grid;
    grid-template-columns: 4fr 1fr;
    grid-template-rows: 1fr 1fr;
    grid-template-areas: "name buttons" "location buttons";

    background-color: rgb(180, 180, 180);
    border-radius: 5px;
    padding: 10px;
    border: 1px solid black;

    margin: 5px;
  }

  .name {
    grid-area: name;
  }

  .location {
    grid-area: location;
  }

  .buttons {
    grid-area: buttons;
    align-self: center;
    justify-self: center;
    display: block;
  }

  .red {
    background-color: red;
  }

  .green {
    background-color: green;
  }

  button {
    width: auto;
    height: 20px;
    padding: 15px;
    text-align: center;
  }

  p {
    margin: 0px
  }
</style>