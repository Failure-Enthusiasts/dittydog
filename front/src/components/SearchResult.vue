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
import SongItem from "./SongItem";
export default {
  components: {SongItem},
  props: {
    results_arr: Array,
  },
  methods: {
    song_confirm: function (id) {
      //hide the search results
      console.log("pretend we added the song " + id);
      this.$emit("addsong");
      // await axios
      //   .post("http://0.0.0.0/confirm", {
      //     song_id: id// (some way to grab the clicked-on song name goes here),
      //   })
      //   .catch(function (error) {
      //     console.log(error);
      //   });
      return 
    },
  }
}
</script>