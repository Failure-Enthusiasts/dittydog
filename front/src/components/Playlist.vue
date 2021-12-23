<template>
  <div id="playlist-results">
    <SongItem
      v-for="search_result in results_arr"
      :key="search_result.song_id"
      v-bind:song_name="search_result.song_name"
      v-bind:artist_name="search_result.artist_name"
      v-bind:album_url="search_result.img_link"
    >
    </SongItem>
  </div>
</template>

<script>
import SongItem from "./SongItem";
export default {
  components: { SongItem },
  props: {
    results_arr: Array,
  },
  methods: {
  },
};
</script>

<style scoped>
#search-results{
  border-style: solid;
  border-radius: 10px;
  border-width: 3px;
}
</style>