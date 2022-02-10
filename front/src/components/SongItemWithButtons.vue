<template>
  <div>

    <div class="voting-components"  @click="vote(song_uri,'up')">
      <Button class="vote-button" arrow_icon="up"></Button>
    </div>
      <div  class="vote_count"><p>{{ vote_count }}</p></div>
      <div class="voting-components" @click="vote(song_uri, 'down')">
      <Button class="vote-button" arrow_icon="down"></Button>
    </div>
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
    song_id: String,
    song_name: String,
    artist_name: String,
    album_name: String,
    album_url: String,
    song_uri: String,
    vote_count: Number
  },
  // vote_direction and song_uri, as JSON (endoint = /vote)
  // fIXME: Bring song_uri to button level!
  methods: {
    vote: async function  (song_uri, vote_direction) {
      console.log(song_uri)
      console.log(vote_direction)
      const response = await axios
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
      console.log(response.data);
      this.$emit('playlist_updated', response.data);
      // this.$emit('playlist_updated');
    },
  },
};
</script>

<style scoped>
.voting-results {
  display: inline-block;
  background-color: rgba(0,0,0,0.05);
  color: black;
  border-radius: 20px;
}
.vote-button {
  display: inline-block;
  padding: 0;
}
.vote_count {
  display: inline-block;
  margin: 0;
  vertical-align: middle;
  padding: 0;
}
div {
  padding: 10px;
}
.voting-components {
  padding: 10px;
  display: inline-block;
  vertical-align: middle;
}

</style>
