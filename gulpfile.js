const gulp = require('gulp');
const fs = require('fs');
const path = require('path');
const xml2js = require('xml2js');
const gulpZip = require('gulp-zip');
const del = require('del'); // Use older del API
const { exec } = require('child_process');

// Clean build directory
gulp.task('clean', () => del(['dist/**', 'cache/**']));

// Run Python tests
gulp.task('test', (done) => {
    exec('.venv/bin/python3 -m pytest tests/ -v', (err, stdout, stderr) => {
        console.log(stdout);
        console.error(stderr);
        done(err);
    });
});

// Copy source files to dist
gulp.task('copy-src', () => {
    return gulp.src([
        'src/**/*',
    ], { base: 'src' })  // Copy src files to root of workflow
        .pipe(gulp.dest('dist/alfred-setapp-search'));
});

// Copy root icon to dist
gulp.task('copy-icon', () => {
    return gulp.src('icon.png')  // Copy root-level icon for Alfred workflow
        .pipe(gulp.dest('dist/alfred-setapp-search'));
});

// Combined copy task
gulp.task('copy', gulp.series('copy-src', 'copy-icon'));

// Create needed directories
gulp.task('create-dirs', (done) => {
    const dirs = ['cache', 'dist'];

    dirs.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });

    done();
});

// Package workflow
gulp.task('package', () => {
    return gulp.src('dist/alfred-setapp-search/**/*')  // Changed: package from root, not src subfolder
        .pipe(gulpZip('alfred-setapp-search.alfredworkflow'))
        .pipe(gulp.dest('dist'));
});

// Copy Python dependencies from virtual environment
gulp.task('copy-deps', (done) => {
    const destDir = 'dist/alfred-setapp-search';

    // First, find the correct site-packages directory
    exec('.venv/bin/python3 -c "import site; print(site.getsitepackages()[0])"', (err, stdout, stderr) => {
        if (err) {
            console.error('Could not find site-packages directory');
            done(err);
            return;
        }

        const sitePackages = stdout.trim();
        const deps = ['requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna'];

        console.log(`Copying Python dependencies from: ${sitePackages}`);

        let completed = 0;
        deps.forEach(dep => {
            exec(`cp -r "${sitePackages}/${dep}"* "${destDir}/" 2>/dev/null || true`, (error, stdout, stderr) => {
                completed++;
                if (error) {
                    console.log(`Note: ${dep} may not exist or was not copied`);
                } else {
                    console.log(`✓ Copied ${dep}`);
                }

                if (completed === deps.length) {
                    done();
                }
            });
        });
    });
});

// Build workflow - Temporarily disabled plist modification tasks
gulp.task('build', gulp.series('clean', 'create-dirs', 'test', 'copy', 'copy-deps', 'package'));

// Watch for changes
gulp.task('watch', () => {
    gulp.watch('src/**/*', gulp.series('copy'));
    // Disabled: gulp.watch('README.md', gulp.series('update-readme-plist'));
});

// Development task - Temporarily disabled plist modification tasks
gulp.task('dev', gulp.series('clean', 'create-dirs', 'copy', 'watch'));

// Default task
gulp.task('default', gulp.series('build'));