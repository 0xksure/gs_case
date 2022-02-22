<script lang="ts">
  import Wave from "images/Waves.svg";
</script>

<div class="navbar">
  <img alt="wave logo" src={Wave} class="wave-icon" />
  <h3>the wave explorer.</h3>
</div>

<style>
  .wave-icon {
    width: 24px;
  }
  .navbar {
    display: flex;
    background-color: black;
    min-height: 2rem;
  }
  .navbar > h3 {
    display: flex;
    color: white;
    align-items: center;
    padding-left: 10px;
    padding-right: 10px;
    margin: 0;
  }
</style>
