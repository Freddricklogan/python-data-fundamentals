/** Report page behaviour: mounts the Executive Shell from the embedded JSON. */
import { mountExecShell } from './exec-shell.js';

const data = JSON.parse(document.getElementById('report-data').textContent);
const money = (n) => (n === null ? 'n/a' : `$${Math.round(n).toLocaleString()}`);

const shell = mountExecShell({
  title: 'Python Data Fundamentals',
  tagline: 'PyBank and PyPoll — four small script repositories — consolidated into one package: CSV parsing that rejects bad input, budget and election analysis with the edge cases the scripts ignored (no changes, all-negative changes, ties), text reports that reproduce the originals byte for byte, a typer CLI, tests, and this static report computed at build time.',
  repo: 'https://github.com/Freddricklogan/python-data-fundamentals',
  pagesUrl: 'https://freddricklogan.github.io/python-data-fundamentals/',
  badges: [{ label: 'typer CLI', tone: 'accent' }, { label: 'Tested edge cases', dot: true }, { label: 'Reports match originals', dot: true }],
  kpis: [
    { label: 'Months analysed', compute: () => data.months, tone: 'accent' },
    { label: 'Net total', compute: () => money(data.netTotal), tone: data.netTotal >= 0 ? 'ok' : 'danger' },
    { label: 'Average monthly change', compute: () => money(data.averageChange) },
    { label: 'Ballots tallied', compute: () => data.totalVotes.toLocaleString() },
    { label: 'Winner', compute: () => data.winner ?? `tie (${data.winners.length})`, tone: data.winner ? 'ok' : 'warn' }
  ],
  tour: [
    { selector: '.md-note', title: 'Same data, one package', body: 'The CSVs are the ones the exercises shipped with. The CLI, the tests and this page all call the same functions; nothing on the page is typed in.' },
    { selector: '#s-budget', title: 'The budget answers, with the swings shown', body: `${data.months} months, net ${money(data.netTotal)}. Greatest increase ${data.greatestIncrease} (${money(data.greatestIncreaseAmount)}), greatest decrease ${data.greatestDecrease} (${money(data.greatestDecreaseAmount)}). The original script could not report an increase if every change was negative; this one can.` },
    { selector: '#s-election', title: 'The tally, with ties made visible', body: `${data.totalVotes.toLocaleString()} ballots across ${data.candidates} candidates and ${data.counties} counties. ${data.winner ? `${data.winner} wins with ${data.winnerShare.toFixed(3)}%` : 'The result is a tie'}; the original scripts would have picked the first name seen and said nothing.` }
  ]
});
shell.refreshKpis();
