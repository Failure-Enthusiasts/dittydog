<template>
  <div class="main-grid">
    <h1 id="title">{{ msg2 }}</h1>
    <div id="search-wrapper">
      <input v-model="spotify_body" @keyup.enter="song_search" placeholder="enter song name" id="search-bar"/>
    </div>
    <div id="wrapper-wrapper">
      <div id="result-wrapper">
        <SearchResult v-bind:results_arr="search_results" v-if="search_mode_on" v-on:addsong="search_mode_on = false, spotify_body = ''" v-on:playlist_update="update_playlist_pls"></SearchResult>
      </div>
      <div id="playlist-wrapper">
        <Playlist v-bind:results_arr="playlist" v-on:playlist_update="update_playlist_pls"></Playlist>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SearchResult from "./SearchResult";
import Playlist from "./Playlist";
export default {
  name: "Main",
  components: {SearchResult, Playlist},
  props: {
    test: String,
    results_arr: Array,
  },
  data() {
    return {
      msg2: "DittyDog",
      spotify_body: "",
      search_results: "",
      search_mode_on: false,
      playlist: [],
    };
  },
  async mounted() {
    try {
      const response = await axios
          .get(
              "http://localhost/get_playlist",
              { withCredentials: true }
          )
          .catch(function(error) {
            console.log(error);
          });
      console.log("PLAYLIST RESPONSE");
      console.log(response.data);
      this.playlist = response.data;
      return response.data;
    } catch (error) {
      console.log(error);
    }
  },
  methods: {
    song_search: async function() {
      try {
        const response = await axios
          .post(
            "http://localhost/search",
            {
              query_string: this.$data.spotify_body,
              limit: 7,
            },
            { withCredentials: true }
          )
          .catch(function(error) {
            console.log(error);
          });
        console.log("RESPONSE");
        console.log(response.data);
        console.log("SEARCH TERM: " + this.$data.spotify_body);
        this.search_results = response.data;
        this.search_mode_on = true;
        return response.data;
      } catch (error) {
        console.log(error);
      }
    },
    update_playlist_pls: function(value){
      console.log("received updated playlist in main")
      console.log(value);
      this.playlist = value;
    },
  },
  
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

#title{
  grid-column: 2;
}

#search-wrapper {
  grid-column: 2;
}

#result-wrapper {
  width: 100%;
  align-self: start;
  position: relative;
  top: -0.3vh;
  z-index: 100;
}

#playlist-wrapper {
  grid-column: 1 / 4;
  width: 100%;
  position: absolute;
  top: 0;
}

#wrapper-wrapper{
  position: relative;
  grid-column: 2;
}

#search-bar{
  margin: 0;
  padding-left: 2vw;
  font-family: inherit;
  width: 100%;
  height: 50px;
  font-size: 30px;
  border-radius: 10px;
  border-width: 3px;
  box-sizing: border-box;
}

#search-button{
  font-family: inherit;
  position:relative; 
  height:52px;
  width: 16%;
  bottom: 6px;
}

h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}

.main-grid {
  display: grid;
  grid-template-columns: 10vw 80vw 10vw;
  /* grid-row-gap: 50px; */
}
</style>
