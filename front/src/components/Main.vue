<template>
  <div class="main-grid">
    <h1>{{ msg2 }}</h1>
    <div>
      <input v-model="spotify_body" placeholder="edit me" />
      <button @click="song_search">Search</button>
      <SearchResult v-bind:results_arr="search_results" v-if="search_mode_on" v-on:addsong="search_mode_on = false, spotify_body = ''"></SearchResult>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SearchResult from "./SearchResult";
// var search_result;
export default {
  name: "Main",
  components: {SearchResult},
  props: {
    test: String,
    results_arr: Array,
  },
  data() {
    return {
      msg2: "hello buddy",
      spotify_body: "",
      search_results: "",
      search_mode_on: false,
    };
  },
  methods: {
    song_search: async function () {
      try {
        const response = await axios
          .post("http://0.0.0.0/search", {
            query_string: this.$data.spotify_body,
            limit: 7,
          })
          .catch(function (error) {
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
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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
  grid-row-gap: 50px;
}
</style>
