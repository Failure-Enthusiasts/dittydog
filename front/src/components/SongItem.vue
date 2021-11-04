<template>
  <div>
    <img :src=album_url>
    <p>
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