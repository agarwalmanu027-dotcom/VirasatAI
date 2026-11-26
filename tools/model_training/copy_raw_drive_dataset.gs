/**
 * Run in Google Apps Script while signed in as manuagarwal885@gmail.com.
 * Copies the shared raw dataset into the user's private raw_copy folder.
 * Run startAutomaticCopy once. It resumes the saved copy each hour and
 * removes its own trigger when the source tree is complete.
 * It does not delete or change any source files.
 */
const SOURCE_RAW_ID = '1Yv06Qg3Pnw94NUkek_oWKxlz83bt87oq';
const DEST_RAW_ID = '1oIFKrlUqwO5tMoHbrtNesmJ8ix5FcNFE';
const STATE_KEY = 'virasat_raw_copy_stack_v1';
const COPY_HANDLER = 'copyRawBatch';

function startAutomaticCopy() {
  const existing = ScriptApp.getProjectTriggers().some(
    trigger => trigger.getHandlerFunction() === COPY_HANDLER);
  if (!existing) {
    ScriptApp.newTrigger(COPY_HANDLER).timeBased().everyHours(1).create();
  }
  console.log(existing ? 'Automatic copy was already scheduled.' :
    'Automatic copy scheduled hourly. Starting one batch now.');
  copyRawBatch();
}

function stopAutomaticCopy() {
  ScriptApp.getProjectTriggers()
    .filter(trigger => trigger.getHandlerFunction() === COPY_HANDLER)
    .forEach(trigger => ScriptApp.deleteTrigger(trigger));
  console.log('Automatic copy stopped; saved copy progress remains intact.');
}

function copyRawBatch() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) {
    console.log('Another copy batch is already running.');
    return;
  }
  const started = Date.now();
  // About 48 minutes/day if the hourly trigger runs every time.
  const stopAfterMs = 2 * 60 * 1000;
  const properties = PropertiesService.getScriptProperties();
  let stack = JSON.parse(properties.getProperty(STATE_KEY) || 'null');
  if (!stack) stack = [{ sourceId: SOURCE_RAW_ID, destId: DEST_RAW_ID, phase: 'files' }];
  let copied = 0;
  let skipped = 0;
  let foldersCreated = 0;

  try {
    while (stack.length && Date.now() - started < stopAfterMs) {
      const frame = stack[stack.length - 1];
      const source = DriveApp.getFolderById(frame.sourceId);
      const dest = DriveApp.getFolderById(frame.destId);

      if (frame.phase === 'files') {
        const iterator = frame.fileToken
          ? DriveApp.continueFileIterator(frame.fileToken)
          : source.getFiles();
        if (!iterator.hasNext()) {
          frame.phase = 'folders';
          delete frame.fileToken;
          continue;
        }
        const file = iterator.next();
        const existing = dest.getFilesByName(file.getName());
        let found = false;
        while (existing.hasNext()) {
          const item = existing.next();
          if (item.getSize() === file.getSize()) {
            found = true;
            break;
          }
        }
        if (found) {
          skipped++;
        } else {
          file.makeCopy(file.getName(), dest);
          copied++;
        }
        if (iterator.hasNext()) {
          frame.fileToken = iterator.getContinuationToken();
        } else {
          frame.phase = 'folders';
          delete frame.fileToken;
        }
      } else {
        const iterator = frame.folderToken
          ? DriveApp.continueFolderIterator(frame.folderToken)
          : source.getFolders();
        if (!iterator.hasNext()) {
          stack.pop();
          continue;
        }
        const child = iterator.next();
        const matches = dest.getFoldersByName(child.getName());
        const hadMatch = matches.hasNext();
        const target = hadMatch
          ? matches.next()
          : dest.createFolder(child.getName());
        if (!hadMatch) foldersCreated++;
        if (iterator.hasNext()) {
          frame.folderToken = iterator.getContinuationToken();
        } else {
          stack.pop();
        }
        stack.push({ sourceId: child.getId(), destId: target.getId(), phase: 'files' });
      }
    }
  } finally {
    if (stack.length) {
      properties.setProperty(STATE_KEY, JSON.stringify(stack));
    } else {
      properties.deleteProperty(STATE_KEY);
      stopAutomaticCopy();
    }
    console.log(JSON.stringify({ copied, skipped, foldersCreated, remainingDepth: stack.length,
      status: stack.length ? 'RUN AGAIN' : 'COMPLETE' }));
    lock.releaseLock();
  }
}
