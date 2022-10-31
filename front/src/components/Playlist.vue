<template>
  <div id="playlist-results">
    <TransitionGroup name="list">
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
    >
    </SongItemWithButtons>
    </TransitionGroup>
  </div>
</template>

<script>
import SongItemWithButtons from "./SongItemWithButtons";
export default {
  data() {
    return {
      session_id: "",
    };
  },
  components: { SongItemWithButtons },
  props: {
    results_arr: Array,
  },
  methods: {
    playlist_update: function(value) {
      this.$emit('playlist_update', value);
      
    },
    // session_id_update: function(value) {
      // this.$emit('session_id', session_id);

    // },
  },
  mounted() {
    console.log(this.$route.query.session_id)
    this.session_id = this.$route.query.session_id
    this.$emit('session_id', this.session_id);
  },
  
};
</script>

<style scoped>
#playlist-results{
  text-align: left
}

.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
  transition: all 2s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
  position: absolute;
}
</style>
