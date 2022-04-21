<template>
  <div id="playlist-results">
    <SongItemWithButtons
      v-for="search_result in results_arr"
      :key="search_result.song_id"
      v-bind:song_name="search_result.song_name"
      v-bind:artist_name="search_result.artist_name"
      v-bind:album_url="search_result.img_link"
      v-bind:song_uri="search_result.song_uri"
      v-bind:vote_count="search_result.vote_count"
      v-bind:locked="search_result.locked"
      v-on:playlist_updated_child="playlist_update"
      v-bind:locked="search_result.locked"
      
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
    playlist_update: function(value) {
      this.$emit('playlist_update', value);
    },
  },
};
</script>

<style scoped>
#playlist-results{
  text-align: left
} 
</style>
