<template>
  <div id="search-results">
    <SongItem
        class="songItemDiv"
      v-for="search_result in results_arr"
      :key="search_result.song_id"
      @click="song_confirm(search_result)"
      v-bind:song_name="search_result.song_name"
      v-bind:artist_name="search_result.artist_name"
      v-bind:album_url="search_result.img_link"
      v-bind:locked="search_result.locked"
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
    song_confirm: async function (search_res) {
      this.$emit("addsong", 'someDataToEmit');
      const response = await axios
        .post(
          "http://localhost/confirm", search_res,
          { withCredentials: true }
        )
        .catch(function (error) {
          console.log(error);
        });
      this.$emit('playlist_update', response.data);
    },
  },
};
</script>

<style scoped>
.songItemDiv {
  cursor: pointer;
}
#search-results{
  border-style: solid;
  border-radius: 10px;
  border-width: 3px;
  background-color: lightyellow;
  text-align: left;
}
</style>