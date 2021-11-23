import compositeTool from "./composite-tool/index.jsx";
import ExternalTool from './external-tool/index.jsx';
import HistoricalDateTool from './historical-date-tool.jsx';
import singleTool from "./single-tool/index.jsx";

import textTool from "./text-tool/index.jsx";
import dateTool from "./date-tool/index.jsx";
import numberTool from "./number-tool/index.jsx";
import textAreaTool from "./text-area-tool/index.jsx";

export default {
  // transcribeTool:   require './transcribe-row-tool'
  compositeTool,
  ExternalTool,
  HistoricalDateTool,
  singleTool,

  textTool, // this will soon be subsumed by single-tool
  dateTool,
  numberTool,
  textAreaTool
};
