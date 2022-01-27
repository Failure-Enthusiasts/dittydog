<template>
  <div id="playlist-results">
    <SongItemWithButtons
      v-for="search_result in results_arr"
      :key="search_result.song_id"
      v-bind:song_name="search_result.song_name"
      v-bind:artist_name="search_result.artist_name"
      v-bind:album_url="search_result.img_link"
      v-bind:song_uri="search_result.song_uri"
    >
    </SongItemWithButtons>
  </div>
</template>

<script>
import SongItemWithButtons from "./SongItemWithButtons";
export default {
  components: { SongItemWithButtons },
  props: {
    results_arr: Array,
  },
  methods: {
  },
};
</script>

<style scoped>
#playlist-results{
  text-align: left
} 
</style>
