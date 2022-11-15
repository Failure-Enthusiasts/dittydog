<template>
  <div>
    <h1>Hello!</h1>
    <div>
      <input v-model="token" placeholder="Enter token"/>
      <button  @click=submitCreds>Log in to session</button>
      <div><a :href=loginlink>Log in to session</a></div>
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
      token: "",
      loginlink: "http://www.google.com"
    };
  },
  async beforeCreate() {
    try {
        const response = await axios
          .get(
            // "http://localhost/get_playlist_id",
            this.$hostname + "/get_login_url",
            { withCredentials: true }
          )
          .catch(function(error) {
            console.log(error);
          });
        console.log(response.data)
        this.loginlink=response.data 
        return;
      } catch (error) {
        console.log(error);
      }
  },
  methods: {
    submitCreds: async function() {
      console.log(this.$data.token)
      try {
        const response = await axios
          .post(
            // "http://localhost/get_playlist_id",
            this.$hostname + "/get_playlist_id",
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
        // router.push({ path: '/', query: { playlist_id: response.data.playlist_id } })
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
