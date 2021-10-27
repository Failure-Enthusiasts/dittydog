<template>
  <div class="main-grid">
    <h1>{{ msg2 }}</h1>
    <div>
      <input v-model="spotify_body" placeholder="edit me" />
      <button @click="song_search">I'm a button</button>
      <p>Message is: {{ spotify_body }}</p>
      <p v-for="search_result in search_results" :key="search_result.song_id">
        {{ search_result.song_name }} -
        {{ search_result.artist_name }}
      </p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
// var search_result;
export default {
  name: "HelloWorld",
  props: {
    msg: String,
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
