const TEST_CASES = [
  // ==========================================================================
  // BASIC SEMANTIC TAGS
  // ==========================================================================
  {
    name: "Simple paragraph",
    input: `<p>Hello world</p>`,
    expected: `<main>
  <p>Hello world</p>
</main>`,
  },
  {
    name: "Heading hierarchy",
    input: `<h1>Title</h1><h2>Subtitle</h2><p>Content</p>`,
    expected: `<main>
  <h1>Title</h1>

  <h2>Subtitle</h2>

  <p>Content</p>
</main>`,
  },
  {
    name: "Link",
    input: `<a href="/about">About Us</a>`,
    expected: `<main>
  <a>About Us</a>
</main>`,
  },
  {
    name: "Button",
    input: `<button type="submit">Submit Form</button>`,
    expected: `<main>
  <button>Submit Form</button>
</main>`,
  },

  // ==========================================================================
  // REGIONS
  // ==========================================================================
  {
    name: "Header with nav",
    input: `<header><h1>Site</h1><nav><a href="/">Home</a></nav></header>`,
    expected: `<header>
  <h1>Site</h1>

  <nav>
    <a>Home</a>
  </nav>
</header>`,
  },
  {
    name: "Footer with content",
    input: `<footer><p>© 2024 Company</p></footer>`,
    expected: `<footer>
  <p>© 2024 Company</p>
</footer>`,
  },

  // ==========================================================================
  // LISTS
  // ==========================================================================
  {
    name: "Nav with heading and list",
    input: `<nav>
      <h5>Company</h5>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
      </ul>
    </nav>`,
    expected: `<nav>
  <h5>Company</h5>

  <ul>
    <li>
      <a>Home</a>
    </li>

    <li>
      <a>About</a>
    </li>
  </ul>
</nav>`,
  },
  {
    name: "Ordered list with step numbers and content",
    input: `<ol>
      <li><span>1</span><h3>Upload Image</h3><p>Drop an image with text.</p></li>
      <li><span>2</span><h3>Analyze</h3><p>We identify fonts.</p></li>
    </ol>`,
    expected: `<ol>
  <li>
    <span>1</span>
    <h3>Upload Image</h3>
    <p>Drop an image with text.</p>
  </li>

  <li>
    <span>2</span>
    <h3>Analyze</h3>
    <p>We identify fonts.</p>
  </li>
</ol>`,
  },
  {
    name: "List item with nested divs (flattens wrappers)",
    input: `<ol>
      <li><div><span>1</span></div><div><h3>Title</h3><p>Description</p></div></li>
    </ol>`,
    expected: `<ol>
  <li>
    <span>1</span>
    <h3>Title</h3>
    <p>Description</p>
  </li>
</ol>`,
  },
  {
    name: "DOM order: heading before list (sequence preserved)",
    input: `<nav>
      <h5>First</h5>
      <ul><li><a href="/">A</a></li></ul>
      <h5>Second</h5>
      <ul><li><a href="/">B</a></li></ul>
    </nav>`,
    expected: `<nav>
  <h5>First</h5>

  <ul>
    <li>
      <a>A</a>
    </li>
  </ul>

  <h5>Second</h5>

  <ul>
    <li>
      <a>B</a>
    </li>
  </ul>
</nav>`,
  },

  // ==========================================================================
  // PROMOTABLE CONTAINERS
  // ==========================================================================
  {
    name: "Div with text (promoted)",
    input: `<div>Standalone text in a div</div>`,
    expected: `<main>
  <div>Standalone text in a div</div>
</main>`,
  },
  {
    name: "Nested divs - innermost carries text",
    input: `<div><div><div>Deep text</div></div></div>`,
    expected: `<main>
  <div>Deep text</div>
</main>`,
  },

  // ==========================================================================
  // NON-TEXT ELEMENTS
  // ==========================================================================
  {
    name: "Image with alt text",
    input: `<img src="hero.jpg" alt="Welcome banner">`,
    expected: `<main>
  <img alt="Welcome banner"/>
</main>`,
  },
  {
    name: "Input with title",
    input: `<input type="email" title="Your email address">`,
    expected: `<main>
  <input title="Your email address" type="email"/>
</main>`,
  },
  {
    name: "Input with placeholder (fallback)",
    input: `<input type="text" placeholder="Enter name">`,
    expected: `<main>
  <input title="Enter name" type="text"/>
</main>`,
  },
  {
    name: "Icon-only button with aria-label",
    input: `<button aria-label="Close menu"><svg></svg></button>`,
    expected: `<main>
  <button aria-label="Close menu"/>
</main>`,
  },
  {
    name: "Icon-only link with aria-label",
    input: `<a href="/" aria-label="Go home"><svg></svg></a>`,
    expected: `<main>
  <a aria-label="Go home"/>
</main>`,
  },

  // ==========================================================================
  // IGNORED CONTENT
  // ==========================================================================
  {
    name: "Script tags ignored",
    input: `<p>Visible</p><script>console.log('hidden')</script>`,
    expected: `<main>
  <p>Visible</p>
</main>`,
  },
  {
    name: "Style tags ignored",
    input: `<style>.foo { color: red; }</style><p>Visible</p>`,
    expected: `<main>
  <p>Visible</p>
</main>`,
  },
  {
    name: "SVG content ignored",
    input: `<p>Before</p><svg><text>SVG Text</text></svg><p>After</p>`,
    expected: `<main>
  <p>Before</p>

  <p>After</p>
</main>`,
  },

  // ==========================================================================
  // EDGE CASES
  // ==========================================================================
  {
    name: "Empty elements produce nothing",
    input: `<p></p><div></div>`,
    expected: ``,
  },
  {
    name: "Whitespace-only content ignored",
    input: `<p>   </p><div>
    </div>`,
    expected: ``,
  },
  {
    name: "Mixed content in paragraph (strong/em flattened)",
    input: `<p>Hello <strong>world</strong> and <em>friends</em></p>`,
    expected: `<main>
  <p>Hello world and friends</p>
</main>`,
  },

  // ==========================================================================
  // REAL-WORLD PATTERNS
  // ==========================================================================
  {
    name: "Card component",
    input: `<article>
      <img src="thumb.jpg" alt="Article thumbnail">
      <h2>Article Title</h2>
      <p>Article description text.</p>
      <a href="/read">Read more</a>
    </article>`,
    expected: `<article>
  <img alt="Article thumbnail"/>

  <h2>Article Title</h2>

  <p>Article description text.</p>

  <a>Read more</a>
</article>`,
  },
  {
    name: "Form with labels and inputs",
    input: `<form>
      <label>Email</label>
      <input type="email" title="Your email">
      <button type="submit">Subscribe</button>
    </form>`,
    expected: `<main>
  <label>Email</label>

  <input title="Your email" type="email"/>

  <button>Subscribe</button>
</main>`,
  },

  // ==========================================================================
  // ADDITIONAL COVERAGE
  // ==========================================================================
  {
    name: "Multiple root regions - no implicit main",
    input: `<header><h1>Site</h1></header><main><p>Content</p></main><footer><p>Footer</p></footer>`,
    expected: `<header>
  <h1>Site</h1>
</header>

<main>
  <p>Content</p>
</main>

<footer>
  <p>Footer</p>
</footer>`,
  },
  {
    name: "LI with plain text (no semantic children)",
    input: `<ul><li>Just plain text</li></ul>`,
    expected: `<ul>
  <li>Just plain text</li>
</ul>`,
  },
  {
    name: "Image without alt ignored",
    input: `<p>Before</p><img src="decorative.jpg"><p>After</p>`,
    expected: `<main>
  <p>Before</p>

  <p>After</p>
</main>`,
  },
  {
    name: "Input without title or placeholder ignored",
    input: `<p>Before</p><input type="text"><p>After</p>`,
    expected: `<main>
  <p>Before</p>

  <p>After</p>
</main>`,
  },
  {
    name: "Button with text ignores aria-label",
    input: `<button aria-label="Submit form">Submit</button>`,
    expected: `<main>
  <button>Submit</button>
</main>`,
  },
  {
    name: "Link with text ignores aria-label",
    input: `<a href="/" aria-label="Navigate home">Home</a>`,
    expected: `<main>
  <a>Home</a>
</main>`,
  },
  {
    name: "Address tag",
    input: `<footer><address>123 Main St, City</address></footer>`,
    expected: `<footer>
  <address>123 Main St, City</address>
</footer>`,
  },
  {
    name: "Aside region",
    input: `<aside><h3>Related</h3><p>Sidebar content</p></aside>`,
    expected: `<aside>
  <h3>Related</h3>

  <p>Sidebar content</p>
</aside>`,
  },
  {
    name: "Deeply nested regions",
    input: `<section><article><h2>Title</h2><section><p>Nested</p></section></article></section>`,
    expected: `<section>
  <article>
    <h2>Title</h2>

    <section>
      <p>Nested</p>
    </section>
  </article>
</section>`,
  },
  {
    name: "Nested lists",
    input: `<ul><li>Parent<ul><li>Child</li></ul></li></ul>`,
    expected: `<ul>
  <li>Parent</li>

  <ul>
    <li>Child</li>
  </ul>
</ul>`,
  },
  {
    name: "Empty alt on image (decorative) ignored",
    input: `<p>Text</p><img src="icon.svg" alt=""><p>More</p>`,
    expected: `<main>
  <p>Text</p>

  <p>More</p>
</main>`,
  },
  {
    name: "Label tag",
    input: `<label for="email">Email address</label>`,
    expected: `<main>
  <label>Email address</label>
</main>`,
  },
  {
    name: "Paragraph with link inside",
    input: `<p>Built by <a href="/">Serbyte Development</a></p>`,
    expected: `<main>
  <p>Built by <a>Serbyte Development</a></p>
</main>`,
  },
  {
    name: "Paragraph with button inside",
    input: `<p>Click <button>here</button> to continue</p>`,
    expected: `<main>
  <p>Click <button>here</button> to continue</p>
</main>`,
  },
  {
    name:"Mobile with complex html",
    input:`<div>
  <div data-ui="global:reviews-modal(closed,open)"></div>
  <div role="dialog" aria-modal="true" aria-label="Reviews">
    <div>
      <div>
        <div>
          <img alt="image-alt" loading="lazy" width="24" height="24" decoding="async" data-nimg="1" />
          <h3>Overall Rating</h3>
        </div>
        <div>
          <div>
            <span>4.9</span>
            <div>
              ★★★★
              <span>★</span>
            </div>
          </div>
          <span>579 verified reviews</span>
        </div>
      </div>
      <button type="button" data-ui="global:reviews-modal(closed,open)">Close</button>
    </div>
    <ul>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="Google reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="google-img" />
          <div>
            <div>
              <img alt="mobile-google-img" />
              <p>Google</p>
            </div>
            <div>
              <span>4.9</span>
              <div>
                <div>
                  <div>
                    ★★★★
                    <span>★</span>
                  </div>
                </div>
                (207)
              </div>
            </div>
          </div>
          <span class="sr-only">Google rating 4.9 out of 5 based on 207 reviews.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="Yelp reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="yelp-img" />
          <div>
            <div>
              <img alt="mobile-yelp-img" />
              <p>Yelp</p>
            </div>
            <div>
              <span>4.8</span>
              <div>
                <div>
                  <div>
                    ★★★★
                    <span>★</span>
                  </div>
                </div>
                (32)
              </div>
            </div>
          </div>
          <span class="sr-only">Yelp rating 4.8 out of 5 based on 32 reviews.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="Facebook reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="facebook-img" />
          <div>
            <div>
              <img alt="mobile-facebook-img" />
              <p>Facebook</p>
            </div>
            <div>
              <span>5.0</span>
              <div>
                <div>
                  <div>★★★★★</div>
                </div>
                (16)
              </div>
            </div>
          </div>
          <span class="sr-only">Facebook rating 5.0 out of 5 based on 16 reviews.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="Angi reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="angi-img" />
          <div>
            <div>
              <img alt="mobile-angi-img" />
              <p>Angi</p>
            </div>
            <div>
              <span>5.0</span>
              <div>
                <div>
                  <div>★★★★★</div>
                </div>
                (12)
              </div>
            </div>
          </div>
          <span class="sr-only">Angi rating 5.0 out of 5 based on 12 reviews.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="BBB reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="bbb-img" />
          <div>
            <div>
              <img alt="mobile-bbb  -img" />
              <p>BBB</p>
            </div>
            <p><span>A+ Rated</span></p>
          </div>
          <span class="sr-only">A+ Rated rated by the BBB.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="Birdeye reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="birdeye-img" />
          <div>
            <div>
              <img alt="mobile-birdeye-img" />
              <p>Birdeye</p>
            </div>
            <div>
              <span>4.9</span>
              <div>
                <div>
                  <div>
                    ★★★★
                    <span>★</span>
                  </div>
                </div>
                (209)
              </div>
            </div>
          </div>
          <span class="sr-only">Birdeye rating 4.9 out of 5 based on 209 reviews.</span>
        </a>
      </li>
      <li>
        <a target="_blank" rel="noopener noreferrer" aria-label="TintFinder reviews (opens in a new tab)">
          <svg>
          </svg>
          <img alt="tintfinder-img" />
          <div>
            <div>
              <img alt="mobile-tintfinder--img" />
              <p>TintFinder</p>
            </div>
            <div>
              <span>4.9</span>
              <div>
                <div>
                  <div>
                    ★★★★
                    <span>★</span>
                  </div>
                </div>
                (103)
              </div>
            </div>
          </div>
          <span class="sr-only">TintFinder rating 4.9 out of 5 based on 103 reviews.</span>
        </a>
      </li>
    </ul>
  </div>
</div>
`,
expected:``
  }
];
