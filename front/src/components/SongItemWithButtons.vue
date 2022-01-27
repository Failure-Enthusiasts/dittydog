<template>
  <div>
    <Button class="voting-results" arrow_icon="up" @click="vote(song_uri,'up')"></Button>
    <Button class="voting-results" arrow_icon="down" @click="vote(song_uri, 'down')"></Button>
    <SongItem
      class="voting-results"
      :key="song_id"
      v-bind:song_name="song_name"
      v-bind:artist_name="artist_name"
      v-bind:album_url="album_url"
    >
    </SongItem>
  </div>
</template>

<script>
import SongItem from "./SongItem";
import Button from "./Button";
import axios from "axios";
export default {
  components: { SongItem, Button },
  props: {
    song_name: String,
    artist_name: String,
    album_name: String,
    album_url: String,
    song_uri: String
  },
  // vote_direction and song_uri, as JSON (endoint = /vote)
  // fIXME: Bring song_uri to button level!
  methods: {
    vote: async function  (song_uri, vote_direction) {
      console.log(song_uri)
      console.log(vote_direction)
      await axios
        .post(
          "http://localhost/vote",
          {
            song_uri: song_uri, // (some way to grab the clicked-on song name goes here),
            vote_direction: vote_direction
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
.voting-results {
  display: inline-block;
}
</style>
