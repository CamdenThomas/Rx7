<!-- The Manual: a title and a blurb until it is planned with him (D-407). -->
<script lang="ts">
  // No state: the page holds its place until the Manual is planned.
</script>

<div class="page narrow manual rise">
  <p class="label">Manual</p>
  <h1>Every fact about this car, exactly as it is today.</h1>
  <p class="blurb">
    One source of truth, arranged however the question needs it — by system, by where it sits on the car, or by
    anything else — and in your pocket anywhere, signal or not. It is being planned with you first, so for now
    this page holds its place.
  </p>
  <img class="art" src="/car/side.webp" alt="The car in profile" />
</div>

<style>
  .manual {
    padding-top: 7vh;
  }
  h1 {
    font-size: clamp(30px, 4vw, 46px);
    font-weight: 700;
    letter-spacing: -0.025em;
    margin: 12px 0 20px;
  }
  .blurb {
    font-size: 17px;
    line-height: 1.6;
    color: var(--text-2);
    max-width: 640px;
  }
  .art {
    display: block;
    width: 100%;
    margin-top: 48px;
    opacity: 0.55;
    mask-image: linear-gradient(180deg, #000 40%, transparent);
  }
</style>
