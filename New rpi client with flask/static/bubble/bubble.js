((main) => {

    this.requestAnimationFrame = (() => {
        return window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function(callback) {
                window.setTimeout(callback, 1000 / 60);
            };
    })();

    main(this, document, Vector2);

})((window, document, v2, undefined) => {

    'use strict';

    const PI = Math.PI,
        TAU = PI * 2;

    const APP_DEFAULTS = {
        particleCount: 600,
        particleColor: 'rgba(200,200,230,0.5)'
    };

    class Particle {
        constructor(size, speed, context, bounds) {
            this.size = size;
            this.ctx = context;
            this.bounds = bounds;
            this.position = new v2();
            this.position.randomize(bounds);
            this.velocity = new v2(0, speed);
            this.velocity.y -= Math.random();
        }

        reset() {
            this.position.y = this.bounds.y + this.size;
            this.position.x = Math.random() * this.bounds.x;
        }

        update() {
            this.position.add(this.velocity);
            if (this.position.y < -this.size) {
                this.reset();
            }
        }
    }

    class App {
        constructor() {
            this.setup();
            this.getCanvas();
            this.resize();
            this.populate();
            this.render();
        }

        setup() {
            let self = this;
            self.props = Object.assign({}, APP_DEFAULTS);
            self.dimensions = new v2();
            window.onresize = () => {
                self.resize();
            };
        }

        getCanvas() {
            this.canvas = {
                back: document.querySelector('.back'),
                mid: document.querySelector('.mid'),
                front: document.querySelector('.front')
            };

            this.ctx = {
                back: this.canvas.back.getContext('2d'),
                mid: this.canvas.mid.getContext('2d'),
                front: this.canvas.front.getContext('2d')
            };
        }

        resize() {
            for (var c in this.canvas) {
                this.canvas[c].width = this.dimensions.x = window.innerWidth;
                this.canvas[c].height = this.dimensions.y = window.innerHeight;
            }
        }

        populate() {
            this.particles = [];
            for (let i = 0; i < this.props.particleCount; i++) {
                let pCtx = i < 300 ? this.ctx.back : i < 500 ? this.ctx.mid : this.ctx.front,
                    size = i < 300 ? 5 : i < 500 ? 8 : 12,
                    speed = i < 300 ? -0.5 : i < 500 ? -1 : -2,
                    particle = new Particle(size, speed, pCtx, this.dimensions);
                this.particles.push(particle);
            }
        }

        render() {
            let self = this;
            self.draw();
            window.requestAnimationFrame(self.render.bind(self));
        }

        draw() {
            for (var c in this.ctx) {
                this.ctx[c].clearRect(0, 0, this.dimensions.x, this.dimensions.y);
            }
            for (let i = 0, len = this.particles.length; i < len; i++) {
                let p = this.particles[i];
                p.update();
                p.ctx.beginPath();
                p.ctx.fillStyle = this.props.particleColor;
                p.ctx.arc(p.position.x, p.position.y, p.size, 0, TAU);
                p.ctx.fill();
                p.ctx.closePath();
            }
        }
    }

    window.onload = () => {
        let app = new App();
    };

});