<template>
  <div>
    <Button class="voting-results"
      v-bind:arrow_direction='up'
    ></Button>
    <Button class="voting-results"
      v-bind:arrow_direction='down'
    ></Button>
    <SongItem
      class="voting-results"
      :key=song_id
      v-bind:song_name=song_name
      v-bind:artist_name=artist_name
      v-bind:album_url=album_url
    >
    </SongItem>
  </div>
</template>

<script>
import SongItem from "./SongItem";
import Button from "./Button";
export default {
  components: { SongItem, Button },
  props: {
    song_name: String,
    artist_name: String,
    album_name: String,
    album_url: String,
  },
  methods: {
  },
};
</script>

<style scoped>
.voting-results{
  display:inline-block
} 
</style>
