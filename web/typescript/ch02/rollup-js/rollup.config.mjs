import terser from '@rollup/plugin-terser';

export default {
	input: 'src/main.js',
	output: [
		{
			file: 'dist/main.bundle.js',
			format: 'cjs'
		},
        {
            file: "dist/main.es.js",
            format: "es"
        },
		{
			file: 'dist/main.min.js',
			format: 'iife',
			name: 'version',
			plugins: [terser()]
		}
	]
};