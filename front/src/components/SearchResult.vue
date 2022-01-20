<template>
  <div id="search-results">
    <SongItem
      v-for="search_result in results_arr"
      :key="search_result.song_id"
      @click="song_confirm(search_result.song_id)"
      v-bind:song_name="search_result.song_name"
      v-bind:artist_name="search_result.artist_name"
      v-bind:album_url="search_result.img_link"
    >
    </SongItem>
  </div>
</template>

<script>
import axios from "axios";
import SongItem from "./SongItem";
export default {
  components: { SongItem },
  props: {
    results_arr: Array,
  },
  methods: {
    song_confirm: async function (song_uri) {
      this.$emit("addsong");
      await axios
        .post(
          "http://localhost/confirm",
          {
            song_uri: song_uri, // (some way to grab the clicked-on song name goes here),
          },
          { withCredentials: true }
        )
        .catch(function (error) {
          console.log(error);
        });
    },
  },
};
</script>

<style scoped>
#search-results{
  border-style: solid;
  border-radius: 10px;
  border-width: 3px;
  background-color: lightyellow;
  text-align: left
}
</style>