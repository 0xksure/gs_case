<script lang="ts">
  import { onMount } from "svelte";
  import type { BoundsReqBody } from "./_types";
  let L;
  let map;
  let boundedPoints = [];
  let warningMessage;
  let waveLayer;
  let calculationTimeoutId;

  function getBounds(map) {
    const boundsCoordinates = map.getBounds();
    const latMax = boundsCoordinates._northEast.lat;
    const lngMax = boundsCoordinates._northEast.lng;
    const latMin = boundsCoordinates._southWest.lat;
    const lngMin = boundsCoordinates._southWest.lng;
    return { latMax, latMin, lngMax, lngMin };
  }

  async function fetchBounds(body: BoundsReqBody) {
    const res = await fetch("http://localhost:5000/bounds", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        body,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (res.status === 204) {
      return {
        data: { features: [] },
        error: "Too many points to load. Please zoom in.",
      };
    }
    if (res.status >= 300) {
      throw "error";
    }
    const data = await res.json();

    return { data, error: "" };
  }

  function onEachPoint(feature, layer) {
    if (feature?.properties?.value) {
      const coord = `(${feature.geometry.coordinates.join(" , ")})`;
      const message = `The max height of a wave at ${coord} is: ${
        Math.round(feature?.properties?.value * 100) / 100
      }m`;
      layer.bindPopup(message);
    }
  }

  function customIconPoint(feature, latlng) {
    const waveSize = feature.properties.size;
    const waveIcon = L.icon({
      iconUrl: `waves-${waveSize}.svg`,
      iconSize: [42, 42],
      iconAnchor: [10, 70],
      popupAnchor: [-3, -76],
    });
    return L.marker(latlng, { icon: waveIcon });
  }

  onMount(async () => {
    const module = await import("leaflet");
    L = module.default;
    map = L.map("map").setView([55, -55], 13);
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      {
        attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
	        &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
        subdomains: "abcd",
        maxZoom: 14,
      }
    ).addTo(map);

    map.on("zoom", async () => {
      clearTimeout(calculationTimeoutId);
      const boundsBody = getBounds(map);
      calculationTimeoutId = setTimeout(async () => {
        const fetchResult = await fetchBounds(boundsBody);
        warningMessage = fetchResult.error;
        boundedPoints = fetchResult?.data?.features ?? [];
      }, 400);
    });

    map.on("move", async () => {
      clearTimeout(calculationTimeoutId);
      const boundsBody = getBounds(map);
      calculationTimeoutId = setTimeout(async () => {
        const fetchResult = await fetchBounds(boundsBody);
        warningMessage = fetchResult.error;
        boundedPoints = fetchResult?.data?.features ?? [];
      }, 400);
    });
  });

  $: if (L && map) {
    if (waveLayer) {
      waveLayer.remove();
    }
    if (boundedPoints.length > 0) {
      waveLayer = L.geoJSON(boundedPoints, {
        onEachFeature: onEachPoint,
        pointToLayer: customIconPoint,
      });
      waveLayer.addTo(map);
    }
  }
</script>

<div class="wave-map">
  {#if warningMessage}
    <div class="warning-message">
      <p>{warningMessage}</p>
    </div>
  {/if}
  <div id="map" />
</div>

<style>
  .wave-map {
    height: 95vh;
    width: 100vw;
  }
  #map {
    height: 100%;
    width: 100%;
  }
  .warning-message {
    position: absolute;
    right: 5%;
    top: 3%;
    z-index: 1000;
    background: rgba(256, 256, 256, 0.5);
    border-radius: 10px;
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .warning-message > p {
    color: red;
    font-weight: 600;
  }
</style>
