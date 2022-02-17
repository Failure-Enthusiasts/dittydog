<template>
    <!-- <p style="font-size: 25px">{{ arrow_icon }};</p> -->
    <div>
      <img v-if="arrow_icon == 'up'" src="@/assets/thumb_icon.svg" style="padding-bottom:10px; padding-right:5px;">
      <img v-if="arrow_icon == 'down'" src="@/assets/thumb_down_icon.svg" style="transform: scaleY(-1); padding-bottom:10px; padding-right:10px;">
    </div>
</template>

<script>
export default {
  props: {
    arrow_icon: String,
  },
};
</script>

<style scoped>
img {
  display: inline-block;
  margin: 0;
  cursor: pointer;
}
</style>
