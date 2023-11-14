<template>
  <div>
    <h1>Redirecting...</h1>
  </div>
</template>

<script>

import axios from "axios";
export default {

  async beforeCreate() {
    try {
        const response = await axios
          .get(
            // "http://localhost/get_playlist_id",
            this.$hostname + "/backend_finish_login", {
              code: this.$route.query.code
            },
            { withCredentials: true }
          )
          .catch(function(error) {
            console.log(error);
          });
        if (response.data.playlist_id){
          console.log("hi in my regex not match")
          this.$router.push({ path: '/playlist', query: { playlist_id: response.data.playlist_id, session_id: response.data.session_id} })
        }
        return;
      } catch (error) {
        console.log(error);
      }
  },

}
