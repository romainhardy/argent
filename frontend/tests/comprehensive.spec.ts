import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const REPORT_DIR = path.join(__dirname, '..', 'test-results', 'findings');
const SCREENSHOTS_DIR = path.join(__dirname, '..', 'test-results', 'screenshots');

// Ensure directories exist
if (!fs.existsSync(REPORT_DIR)) fs.mkdirSync(REPORT_DIR, { recursive: true });
if (!fs.existsSync(SCREENSHOTS_DIR)) fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

interface Finding {
  component: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  screenshot?: string;
  timestamp: string;
}

const findings: Finding[] = [];

function addFinding(finding: Omit<Finding, 'timestamp'>) {
  findings.push({
    ...finding,
    timestamp: new Date().toISOString(),
  });
}

async function takeScreenshot(page: Page, name: string): Promise<string> {
  const filename = `${name}-${Date.now()}.png`;
  const filepath = path.join(SCREENSHOTS_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  return filename;
}

async function checkForErrors(page: Page): Promise<string[]> {
  const errors: string[] = [];

  // Check for error boundaries (blue screens)
  const errorBoundary = await page.locator('.bg-blue-500, .bg-blue-600, [class*="error-boundary"]').count();
  if (errorBoundary > 0) {
    errors.push('Error boundary (blue screen) detected');
  }

  // Check for error states
  const errorStates = await page.locator('[class*="error"], [class*="Error"]').count();
  if (errorStates > 0) {
    const errorText = await page.locator('[class*="error"], [class*="Error"]').first().textContent();
    if (errorText && !errorText.includes('No error')) {
      errors.push(`Error state found: ${errorText?.slice(0, 100)}`);
    }
  }

  return errors;
}

test.describe('API Health Tests', () => {
  test('Backend API is healthy', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/health');
    const status = response.status();

    if (status === 200) {
      const data = await response.json();
      addFinding({
        component: 'Backend API',
        status: 'pass',
        message: `API healthy. Version: ${data.version}`,
      });
    } else {
      addFinding({
        component: 'Backend API',
        status: 'fail',
        message: `API returned status ${status}`,
      });
    }

    expect(status).toBe(200);
  });

  test('Analysis list endpoint works', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/analysis?limit=5');
    const status = response.status();

    if (status === 200) {
      const data = await response.json();
      addFinding({
        component: 'Analysis List API',
        status: 'pass',
        message: `Returns ${data.analyses?.length || 0} analyses`,
      });
    } else {
      addFinding({
        component: 'Analysis List API',
        status: 'fail',
        message: `Status ${status}`,
      });
    }

    expect(status).toBe(200);
  });

  test('Price history endpoint works', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/symbols/AAPL/history?period=1mo');
    const status = response.status();

    if (status === 200) {
      const data = await response.json();
      addFinding({
        component: 'Price History API',
        status: 'pass',
        message: `Returns ${data.data?.length || 0} price bars for AAPL`,
      });
    } else {
      addFinding({
        component: 'Price History API',
        status: 'fail',
        message: `Status ${status}`,
      });
    }

    expect(status).toBe(200);
  });
});

test.describe('Dashboard Page Tests', () => {
  test('Dashboard loads without errors', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const screenshot = await takeScreenshot(page, 'dashboard');
    const errors = await checkForErrors(page);

    if (errors.length > 0) {
      addFinding({
        component: 'Dashboard',
        status: 'fail',
        message: errors.join('; '),
        screenshot,
      });
    } else {
      addFinding({
        component: 'Dashboard',
        status: 'pass',
        message: 'Loads successfully',
        screenshot,
      });
    }

    expect(errors.length).toBe(0);
  });

  test('Dashboard displays navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const nav = await page.locator('nav, [role="navigation"], aside').first();
    const hasNav = await nav.count() > 0;

    if (hasNav) {
      addFinding({
        component: 'Navigation',
        status: 'pass',
        message: 'Navigation present',
      });
    } else {
      addFinding({
        component: 'Navigation',
        status: 'warning',
        message: 'Navigation element not found',
      });
    }
  });
});

test.describe('Charts Page Tests', () => {
  test('Charts page loads for AAPL', async ({ page }) => {
    await page.goto('/charts?symbol=AAPL');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Wait for chart to render

    const screenshot = await takeScreenshot(page, 'charts-aapl');
    const errors = await checkForErrors(page);

    // Check if chart container exists
    const chartContainer = await page.locator('canvas, [class*="chart"], [class*="Chart"]').count();

    if (errors.length > 0) {
      addFinding({
        component: 'Charts Page',
        status: 'fail',
        message: errors.join('; '),
        screenshot,
      });
    } else if (chartContainer === 0) {
      addFinding({
        component: 'Charts Page',
        status: 'warning',
        message: 'Page loaded but no chart elements found',
        screenshot,
      });
    } else {
      addFinding({
        component: 'Charts Page',
        status: 'pass',
        message: `Loaded with ${chartContainer} chart element(s)`,
        screenshot,
      });
    }

    expect(errors.length).toBe(0);
  });

  test('Symbol search works on Charts page', async ({ page }) => {
    await page.goto('/charts?symbol=AAPL');
    await page.waitForLoadState('networkidle');

    // Find search input
    const searchInput = page.locator('input[type="text"], input[placeholder*="search" i], input[placeholder*="symbol" i]').first();
    const hasSearch = await searchInput.count() > 0;

    if (hasSearch) {
      await searchInput.fill('MSFT');
      await searchInput.press('Enter');
      await page.waitForTimeout(2000);

      const screenshot = await takeScreenshot(page, 'charts-search-msft');
      const errors = await checkForErrors(page);

      if (errors.length > 0) {
        addFinding({
          component: 'Charts Symbol Search',
          status: 'fail',
          message: errors.join('; '),
          screenshot,
        });
      } else {
        addFinding({
          component: 'Charts Symbol Search',
          status: 'pass',
          message: 'Search functionality works',
          screenshot,
        });
      }
    } else {
      addFinding({
        component: 'Charts Symbol Search',
        status: 'warning',
        message: 'Search input not found',
      });
    }
  });
});

test.describe('Analysis Page Tests', () => {
  test('Analysis page loads', async ({ page }) => {
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');

    const screenshot = await takeScreenshot(page, 'analysis-page');
    const errors = await checkForErrors(page);

    if (errors.length > 0) {
      addFinding({
        component: 'Analysis Page',
        status: 'fail',
        message: errors.join('; '),
        screenshot,
      });
    } else {
      addFinding({
        component: 'Analysis Page',
        status: 'pass',
        message: 'Loads successfully',
        screenshot,
      });
    }

    expect(errors.length).toBe(0);
  });

  test('Can start new analysis', async ({ page }) => {
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');

    // Click New Analysis button if present
    const newAnalysisBtn = page.locator('button:has-text("New Analysis"), button:has-text("Start Analysis")').first();
    if (await newAnalysisBtn.count() > 0) {
      await newAnalysisBtn.click();
      await page.waitForTimeout(500);
    }

    // Find and fill the symbols input
    const symbolsInput = page.locator('input[placeholder*="symbol" i], input[placeholder*="AAPL" i]').first();

    if (await symbolsInput.count() > 0) {
      await symbolsInput.fill('AAPL');

      // Click start button
      const startBtn = page.locator('button:has-text("Start"), button:has-text("Analyze")').first();
      if (await startBtn.count() > 0) {
        await startBtn.click();
        await page.waitForTimeout(5000); // Wait for analysis

        const screenshot = await takeScreenshot(page, 'analysis-started');
        const errors = await checkForErrors(page);

        if (errors.length > 0) {
          addFinding({
            component: 'Start Analysis',
            status: 'fail',
            message: errors.join('; '),
            screenshot,
          });
        } else {
          addFinding({
            component: 'Start Analysis',
            status: 'pass',
            message: 'Analysis started successfully',
            screenshot,
          });
        }
      }
    } else {
      addFinding({
        component: 'Start Analysis',
        status: 'warning',
        message: 'Symbols input not found',
      });
    }
  });

  test('Analysis results display correctly', async ({ page }) => {
    // First get an existing analysis ID
    const response = await page.request.get('http://localhost:8000/api/v1/analysis?limit=1');
    const data = await response.json();

    if (data.analyses && data.analyses.length > 0) {
      const analysisId = data.analyses[0].id;
      await page.goto(`/analysis?id=${analysisId}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      const screenshot = await takeScreenshot(page, 'analysis-results');
      const errors = await checkForErrors(page);

      // Check for recommendation cards, risk metrics, etc.
      const hasRecommendations = await page.locator('[class*="recommendation" i], [class*="Recommendation" i]').count() > 0;
      const hasRisk = await page.locator('[class*="risk" i], [class*="Risk" i]').count() > 0;

      if (errors.length > 0) {
        addFinding({
          component: 'Analysis Results Display',
          status: 'fail',
          message: errors.join('; '),
          screenshot,
        });
      } else {
        addFinding({
          component: 'Analysis Results Display',
          status: 'pass',
          message: `Results displayed. Recommendations: ${hasRecommendations}, Risk: ${hasRisk}`,
          screenshot,
        });
      }
    } else {
      addFinding({
        component: 'Analysis Results Display',
        status: 'warning',
        message: 'No existing analyses to test',
      });
    }
  });
});

test.describe('Portfolio Page Tests', () => {
  test('Portfolio page loads', async ({ page }) => {
    await page.goto('/portfolio');
    await page.waitForLoadState('networkidle');

    const screenshot = await takeScreenshot(page, 'portfolio-page');
    const errors = await checkForErrors(page);

    if (errors.length > 0) {
      addFinding({
        component: 'Portfolio Page',
        status: 'fail',
        message: errors.join('; '),
        screenshot,
      });
    } else {
      addFinding({
        component: 'Portfolio Page',
        status: 'pass',
        message: 'Loads successfully',
        screenshot,
      });
    }
  });
});

test.describe('Backtest Page Tests', () => {
  test('Backtest page loads', async ({ page }) => {
    await page.goto('/backtest');
    await page.waitForLoadState('networkidle');

    const screenshot = await takeScreenshot(page, 'backtest-page');
    const errors = await checkForErrors(page);

    if (errors.length > 0) {
      addFinding({
        component: 'Backtest Page',
        status: 'fail',
        message: errors.join('; '),
        screenshot,
      });
    } else {
      addFinding({
        component: 'Backtest Page',
        status: 'pass',
        message: 'Loads successfully',
        screenshot,
      });
    }
  });
});

test.describe('Console Error Detection', () => {
  test('No JavaScript errors on Dashboard', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', err => {
      consoleErrors.push(err.message);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (consoleErrors.length > 0) {
      addFinding({
        component: 'Dashboard Console',
        status: 'fail',
        message: `${consoleErrors.length} JS errors: ${consoleErrors.slice(0, 3).join('; ')}`,
      });
    } else {
      addFinding({
        component: 'Dashboard Console',
        status: 'pass',
        message: 'No JavaScript errors',
      });
    }
  });

  test('No JavaScript errors on Analysis page', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', err => {
      consoleErrors.push(err.message);
    });

    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (consoleErrors.length > 0) {
      addFinding({
        component: 'Analysis Console',
        status: 'fail',
        message: `${consoleErrors.length} JS errors: ${consoleErrors.slice(0, 3).join('; ')}`,
      });
    } else {
      addFinding({
        component: 'Analysis Console',
        status: 'pass',
        message: 'No JavaScript errors',
      });
    }
  });
});

test.afterAll(async () => {
  // Generate findings report
  const report = {
    generatedAt: new Date().toISOString(),
    summary: {
      total: findings.length,
      passed: findings.filter(f => f.status === 'pass').length,
      failed: findings.filter(f => f.status === 'fail').length,
      warnings: findings.filter(f => f.status === 'warning').length,
    },
    findings,
  };

  const reportPath = path.join(REPORT_DIR, 'test-findings.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // Generate markdown report
  let markdown = `# Test Findings Report\n\n`;
  markdown += `Generated: ${report.generatedAt}\n\n`;
  markdown += `## Summary\n\n`;
  markdown += `| Status | Count |\n|--------|-------|\n`;
  markdown += `| ✅ Passed | ${report.summary.passed} |\n`;
  markdown += `| ❌ Failed | ${report.summary.failed} |\n`;
  markdown += `| ⚠️ Warnings | ${report.summary.warnings} |\n`;
  markdown += `| **Total** | ${report.summary.total} |\n\n`;

  markdown += `## Detailed Findings\n\n`;

  for (const finding of findings) {
    const icon = finding.status === 'pass' ? '✅' : finding.status === 'fail' ? '❌' : '⚠️';
    markdown += `### ${icon} ${finding.component}\n\n`;
    markdown += `**Status:** ${finding.status.toUpperCase()}\n\n`;
    markdown += `**Message:** ${finding.message}\n\n`;
    if (finding.screenshot) {
      markdown += `**Screenshot:** ${finding.screenshot}\n\n`;
    }
    markdown += `---\n\n`;
  }

  const markdownPath = path.join(REPORT_DIR, 'test-findings.md');
  fs.writeFileSync(markdownPath, markdown);

  console.log(`\n📊 Test report saved to: ${reportPath}`);
  console.log(`📄 Markdown report saved to: ${markdownPath}`);
});
