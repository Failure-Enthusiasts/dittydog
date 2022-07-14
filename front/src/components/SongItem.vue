<template>
  <div>
    <img :src=album_url class="albumArt">
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
    locked: Boolean
  },
}
</script>

<style scoped>
.albumArt {
  width:40px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 10px;
  border-radius: 20px;
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
