<template >
  <div class="main-grid">
    <h1 id="title">{{ msg2 }}</h1>
    <h2> {{session_id}} </h2>
    <div id="search-wrapper">
      <input v-model="spotify_body" @keyup="song_search" placeholder="enter song name" id="search-bar"/>
      <a :href = playlist_link target = "_blank"> <button :class="{ playButtonHidden: play_button_hidden }" @click="start_polling">Start Playlist</button></a>
    </div>
    <div id="wrapper-wrapper">
      <div id="result-wrapper">
        <SearchResult v-bind:results_arr="search_results" v-show="search_mode_on" v-on:addsong="search_mode_on = false, spotify_body = ''" v-on:playlist_update="update_playlist_pls"></SearchResult>
      </div>
      <div id="playlist-wrapper">
        <Playlist v-bind:results_arr="playlist" v-on:playlist_update="update_playlist_pls" v-on:session_id="session_update_pls"></Playlist>
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
    var urlParams = new URLSearchParams(window.location.search);
    var playlist_id = urlParams.get('playlist_id');
    return {
      isConnected: false,
      socketMessage: '',
      msg2: "DittyDog",
      session_id: "",
      play_button_hidden: true,
      spotify_body: "",
      search_results: "",
      playlist_id: playlist_id,
      search_mode_on: false,
      playlist: [],
      playlist_link: `https://open.spotify.com/playlist/${urlParams.get('playlist_id')}`
    };
  },

  sockets: {
    connect() {
      // Fired when the socket connects.
      this.isConnected = true;
    },

    disconnect() {
      this.isConnected = false;
    },

    message(data) {
      console.log('this method was fired by the socket server. eg: io.emit("customEmit", data)');
      console.log(data);
    },

    incomingData(data) {
      console.log('this method was fired by the socket server, incomingData. eg: io.emit("customEmit", data)');
      console.log(data);

      console.log('Grabbing playlist manually!');
      const response = this.manual_playlist_request();
      console.log(response);

    },

    // Fired when the server sends something on the "messageChannel" channel.
    messageChannel(data) {
      this.socketMessage = data

    }
  },

  async mounted() {
    this.$socket.on('incomingData', (data) => {
      console.log(data);
    });
    this.manual_playlist_request();
  //   try {
  //   const response = await axios
  //       .get(
  //           "http://localhost/get_playlist",
  //           { withCredentials: true }
  //       )
  //       .catch(function(error) {
  //         console.log(error);
  //       });


  //   this.playlist = response.data;
  //   this.play_button_hidden = this.playlist.length < 5;
  //   return response.data;
  // } catch (error) {

  // }
    
  },
  methods: {
    song_search: async function() {

      if (this.$data.spotify_body != ""){
        try {
          const response = await axios
            .post(
              this.$hostname + "/search",
              {
                query_string: this.$data.spotify_body,
                limit: 7,
              },
              { withCredentials: true }
            )
            .catch(function(error) {
              console.log(error);
            });


          this.search_results = response.data;
          this.search_mode_on = true;
          return response.data;
        } catch (error) {
          console.log(error);
        }
      } else {
        this.search_mode_on = false;
      }
    },
    update_playlist_pls: function(value){
      console.log("received updated playlist in main")

      this.playlist = value;
      this.play_button_hidden = value.length < 2;
    },
    session_update_pls: function(value){
      console.log("received updated session_id in main")

      this.session_id = value;
      // this.play_button_hidden = value.length < 2;
    },
    exit_search: function(e){
      if(e.target.id != 'search-bar') {
        this.search_mode_on = false;
      }
    },
    start_polling: async function(){
      try {
          await axios
            .post(
              this.$hostname + "/polling_and_pruning",
              {
                song_uri: 'yes', // (some way to grab the clicked-on song name goes here
                vote_direction: 'sure'
              },
              { withCredentials: true }
            )
            .catch(function(error) {
              console.log(error);
            });
          
          return
        } catch (error) {
          console.log(error);
        }
    },
    manual_playlist_request: async function(){
      try {
          const response = await axios
              .get(
                  this.$hostname + "/get_playlist",
                  { withCredentials: true }
              )
              .catch(function(error) {
                console.log(error);
              });


          this.playlist = response.data;
          // this.play_button_hidden = this.playlist.length < 5;
          return response.data;
        } catch (error) {
          console.log(error);
        }
    }
  },
  
  
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

#title { 
  grid-column: 2;
}

#spotify-playlist-button {
  grid-column: 2;
  /*background-color: #1DB954;*/
  width: 80px;
  /*padding: 5px;*/
  place-self: center;
  /*margin: 10px;*/
  /*border-radius: 10px;*/
  /*border-width: 3px;*/
  /*font-family: inherit;*/
}

#button-text {
  font-size: 24px;
  color: white;
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
  text-decoration: none;
}

.main-grid {
  display: grid;
  grid-template-columns: 10vw 80vw 10vw;
  /* grid-row-gap: 50px; */
}

#hiding-box{
  height: 50px;
  width: 100px;
  color: red;
}

.playButtonHidden {
  display: none
}
</style>
