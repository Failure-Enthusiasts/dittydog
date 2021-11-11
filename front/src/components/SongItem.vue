<template>
  <div>
    <img :src=album_url>
    <p class="itemwrapper">
      {{ song_name }} -
      {{ artist_name }}
    </p>
  </div>
</template>

<script>
export default {
  props: {
    song_name: String,
    artist_name: String,
    album_name: String,
    album_url: String,
  },
}
</script>

<style scoped>
img {
  width:40px;
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
