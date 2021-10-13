<template>
  <div class="main-grid">
    <h1>{{ msg2 }}</h1>
    <div>
     <input v-model="spotify_body" placeholder="edit me">
     <button @click="doSomething">I'm a button</button>
      <p>Message is: {{ spotify_body }}</p>     
    
    </div>
   
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }, 
  data() {
    return{
      msg2:'hello buddy',
      spotify_body: ''
    }
  },
  methods: {
    async doSomething(){
      try {
            const response = await axios.get(
              "http://jsonplaceholder.typicode.com/posts"
            );
            // JSON responses are automatically parsed.
            // this.posts = response.data;
            console.log(this.$data.spotify_body)
            console.log(response)
          } catch (error) {
            console.log(error);
          }
    }
  }
}
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
grid-row-gap:50px; 
}
</style>
