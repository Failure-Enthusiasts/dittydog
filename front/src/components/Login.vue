<template>
  <div>
    <h1>Hello!</h1>
    <div>
      <input v-model="token" placeholder="Enter token"/>
      <button  @click=submitCreds>Log in to session</button>
      <!-- <router-link to="/">Log in to session</router-link> -->
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {

  props: {

  },
  data() {
    return {
      token: ""
    };
  },
  methods: {
    submitCreds: async function() {
      console.log(this.$data.token)
      try {
        const response = await axios
          .post(
            "http://localhost/get_playlist_id",
            {
              query_string: this.$data.token
            },
            { withCredentials: true }
          )
          .catch(function(error) {
            console.log(error);
          });
        console.log(response.data)
        // this.search_results = response.data;
        this.$router.push({ path: '/', query: { playlist_id: response.data.playlist_id } })
        return;
      } catch (error) {
        console.log(error);
      }
    }

  },
};
</script>

<style scoped>

</style>
