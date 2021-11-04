<template>
  <div class="main-grid">
    <h1>{{ msg2 }}</h1>
    <div>
      <input v-model="spotify_body" placeholder="edit me" />
      <button @click="song_search">Search</button>
      <SearchResult v-bind:results_arr="search_results"></SearchResult>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SearchResult from "./SearchResult";
// var search_result;
export default {
  name: "HelloWorld",
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
        return response.data;
      } catch (error) {
        console.log(error);
      }
    },
    song_confirm: async function (id) {
      //hide the search results


      console.log("pretend we added the song " + id)
      // await axios
      //   .post("http://0.0.0.0/confirm", {
      //     song_id: id// (some way to grab the clicked-on song name goes here),
      //   })
      //   .catch(function (error) {
      //     console.log(error);
      //   });
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
