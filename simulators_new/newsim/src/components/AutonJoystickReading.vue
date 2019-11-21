<template>
  <div class="wrap">
    <div>forward_back: {{Joystick.forward_back}}</div>
    <div>left_right: {{Joystick.left_right}}</div>
    <div>dampen: {{Joystick.dampen}}</div>
    <div>kill: {{Joystick.kill}}</div>
    <div>restart: {{Joystick.restart}}</div>
  </div>
</template>

<script>
export default {
  props: {
    Joystick: {
      type: Object,
      required: true
    },
  }
}
/* if you seek the joystick error, here are some notes:
it's a required prop, but that may not necessarily be an error per se
if the autonomy system gives it valid input
if it remains an error, tweak this file. if not, delete this comment */
</script>

<style scoped>
  .wrap {
      padding: 0px;
      padding-left: 5px;
      padding-right: 5px;
      border: none;
  }
</style>

