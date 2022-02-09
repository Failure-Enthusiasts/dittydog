<template>
  <div>
    <!-- <p style="font-size: 25px">{{ arrow_icon }};</p> -->
    <p v-if="arrow_icon == 'up'"> &#128314; </p>
    <p v-if="arrow_icon == 'down'"> &#128315; </p>
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
  width: 40px;
  display: inline-block;
  vertical-align: middle;
  padding-right: 10px;
}
.itemwrapper {
  display: inline;
  font-size: 25px;
  vertical-align: middle;
}
div {
  padding: 10px;
}
</style>
