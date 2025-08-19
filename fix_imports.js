const fs = require('fs');
const path = require('path');

const componentsDir = path.join(__dirname, 'social-trend-analyzer', 'src');

function findAndReplaceInTsxFiles(directory) {
    const files = fs.readdirSync(directory);

    files.forEach(file => {
        const fullPath = path.join(directory, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            findAndReplaceInTsxFiles(fullPath);
        } else if (fullPath.endsWith('.tsx')) {
            try {
                let content = fs.readFileSync(fullPath, 'utf8');
                const searchString = 'from "@/lib/utils"';
                const replaceString = 'from "@/lib/utils.ts"';

                if (content.includes(searchString)) {
                    const newContent = content.replace(new RegExp(searchString, 'g'), replaceString);
                    fs.writeFileSync(fullPath, newContent, 'utf8');
                    console.log(`Updated import in: ${fullPath}`);
                }
            } catch (error) {
                console.error(`Failed to process file ${fullPath}:`, error);
            }
        }
    });
}

console.log('Starting import fix script...');
findAndReplaceInTsxFiles(componentsDir);
console.log('Import fix script finished.');