const fs = require('fs');
const path = require('path');

const pages = [
  'LandingPage', 'LoginPage', 'DashboardPage', 'RepositoriesPage', 
  'CommitHistoryPage', 'CommitDetailPage', 'AnalyticsPage', 'ContributorsPage',
  'RecommendationsPage', 'ActivityPage', 'SettingsPage', 'ModelPerformancePage', 'DemoPage'
];

const dir = path.join(__dirname, 'frontend/src/pages');
if (!fs.existsSync(dir)){
    fs.mkdirSync(dir, { recursive: true });
}

pages.forEach(page => {
  const content = `import React from 'react';\n\nexport default function ${page}() {\n  return (\n    <div className="page-wrapper">\n      <div className="page-header">\n        <div className="page-title-group">\n          <h1 className="page-title">${page.replace('Page', '')}</h1>\n        </div>\n      </div>\n      <div className="card card-padding">\n        <p>This is the ${page} component.</p>\n      </div>\n    </div>\n  );\n}\n`;
  fs.writeFileSync(path.join(dir, `${page}.tsx`), content);
});

console.log('Pages generated.');
